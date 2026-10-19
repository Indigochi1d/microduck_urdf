#!/usr/bin/env python3
"""Smoke tests for the Microduck URDF and its xacro entry point."""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
URDF = ROOT / 'urdf' / 'microduck.urdf'
XACRO = ROOT / 'urdf' / 'microduck.urdf.xacro'

ACTUATED_JOINTS = {
    f'{side}_{j}' for side in ('left', 'right')
    for j in ('hip_yaw', 'hip_roll', 'hip_pitch', 'knee', 'ankle')
} | {'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll'}
SENSOR_FRAMES = {'imu', 'left_foot', 'right_foot', 'head_camera', 'tof', 'head_imu', 'mouth_tip'}


def run_xacro(*args):
    result = subprocess.run(['xacro', str(XACRO), *args], capture_output=True, text=True,
                            timeout=60)
    assert result.returncode == 0, result.stderr
    return ET.fromstring(result.stdout)


@pytest.fixture(scope='module')
def urdf():
    return ET.parse(URDF).getroot()


def test_joint_set(urdf):
    revolute = {j.get('name') for j in urdf.findall('joint') if j.get('type') == 'revolute'}
    fixed = {j.get('name') for j in urdf.findall('joint') if j.get('type') == 'fixed'}
    assert revolute == ACTUATED_JOINTS
    assert fixed == {f'{s}_joint' for s in SENSOR_FRAMES}


def test_joint_limits_are_valid(urdf):
    for joint in urdf.findall('joint'):
        if joint.get('type') != 'revolute':
            continue
        limit = joint.find('limit')
        assert limit is not None, f'{joint.get("name")} has no <limit>'
        assert float(limit.get('lower')) < float(limit.get('upper')), joint.get('name')
        assert float(limit.get('effort')) > 0 and float(limit.get('velocity')) > 0


def test_tree_is_connected(urdf):
    links = {l.get('name') for l in urdf.findall('link')}
    children = [j.find('child').get('link') for j in urdf.findall('joint')]
    parents = {j.find('parent').get('link') for j in urdf.findall('joint')}
    assert len(children) == len(set(children)), 'a link has more than one parent'
    assert links - set(children) == {'base_link'}
    assert parents <= links and set(children) <= links


def test_body_links_have_inertia(urdf):
    total = 0.0
    for link in urdf.findall('link'):
        if link.find('visual') is None:
            continue  # sensor frames carry no mass
        inertial = link.find('inertial')
        assert inertial is not None, f'{link.get("name")} has no <inertial>'
        mass = float(inertial.find('mass').get('value'))
        i = inertial.find('inertia').attrib
        assert mass > 0, link.get('name')
        assert min(float(i['ixx']), float(i['iyy']), float(i['izz'])) > 0, link.get('name')
        total += mass
    assert 0.6 < total < 0.8  # Microduck is spec'd at under 800 g


def test_meshes_exist_and_are_all_used(urdf):
    used = {Path(m.get('filename')).name for m in urdf.iter('mesh')}
    on_disk = {p.name for p in (ROOT / 'meshes').glob('*.stl')}
    assert used <= on_disk, f'missing: {used - on_disk}'
    assert on_disk <= used, f'unused: {on_disk - used}'


def test_xacro_matches_standalone_urdf(urdf):
    def canonical(robot):
        for mesh in robot.iter('mesh'):
            mesh.set('filename', Path(mesh.get('filename')).name)
        return ET.canonicalize(ET.tostring(robot, encoding='unicode'), strip_text=True)

    generated = run_xacro()
    generated.attrib.pop('name', None)
    standalone = ET.fromstring(ET.tostring(urdf))
    standalone.attrib.pop('name', None)
    assert canonical(generated) == canonical(standalone)


def test_xacro_collision_toggle():
    assert list(run_xacro().iter('collision'))
    assert not list(run_xacro('collision:=false').iter('collision'))
