"""Build deliverables from current source strips using the bundled Pets tools."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATES = dict(zip(
    ('idle', 'running-right', 'running-left', 'waving', 'jumping',
     'failed', 'waiting', 'running', 'review'), (6, 8, 8, 4, 5, 8, 6, 6, 6)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(scripts, name, *args):
    result = subprocess.run(
        [sys.executable, str(scripts / name), *map(str, args)],
        env={**os.environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'},
        capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{name} failed:\n{result.stdout}\n{result.stderr}')
    print(f'  {name}: done', flush=True)


def save_gif(path, frames, duration):
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, disposal=2, optimize=False)


def build(outfit, scripts):
    folder = ROOT / outfit
    source = folder / '创作素材'
    source_files = ['三视图.jpg', '基础造型.png', *[f'{s}.png' for s in STATES],
                    'look-cardinals.png', 'look-row-9.png', 'look-row-10.png']
    inputs = [{'file': f'创作素材/{f}', 'sha256': sha(source / f)} for f in source_files]
    print(f'Building {outfit}', flush=True)
    temporary_root = (ROOT / 'tmp').resolve()
    temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bluefish-build-', dir=temporary_root) as tmp:
        work = Path(tmp)
        assert work.resolve().is_relative_to(temporary_root)
        frames = work / '逐帧PNG'
        previews = work / '预览'
        reports = work / '验证'
        reports.mkdir()
        # Fail on touching/merged poses, rather than silently slicing equal slots.
        sys.path.insert(0, str(scripts))
        from extract_strip_frames import connected_components, remove_chroma_background
        for state, count in {**STATES, 'look-row-9': 8, 'look-row-10': 8}.items():
            with Image.open(source / f'{state}.png') as image:
                keyed = remove_chroma_background(image, (0, 255, 0), 96)
            components = connected_components(keyed)
            largest = max(c['area'] for c in components)
            groups = [c for c in components if c['area'] >= max(120, largest * .2)]
            if len(groups) != count:
                raise RuntimeError(f'{outfit}/{state}: expected {count} separated poses, found {len(groups)}')
        run(scripts, 'extract_strip_frames.py', '--decoded-dir', source,
            '--output-dir', frames, '--method', 'components', '--chroma-key', '#00FF00')
        run(scripts, 'inspect_frames.py', '--frames-root', frames,
            '--json-out', reports / 'review.json', '--require-components')
        run(scripts, 'compose_atlas.py', '--frames-root', frames, '--output', work / 'base.png')
        run(scripts, 'assemble_extended_atlas.py', '--base-atlas', work / 'base.png',
            '--look-row-9', source / 'look-row-9.png', '--registered-row-output', work / 'row9.png',
            '--registration-manifest-output', work / 'registration.json')
        run(scripts, 'assemble_extended_atlas.py', '--base-atlas', work / 'base.png',
            '--registered-row-9', work / 'row9.png', '--row-9-registration', work / 'registration.json',
            '--look-row-10', source / 'look-row-10.png', '--output', work / 'raw.png')
        run(scripts, 'despill_chroma_edges.py', work / 'raw.png', '--output', work / 'spritesheet.png',
            '--chroma-key', '#00FF00', '--json-out', reports / 'chroma-despill-extended.json')
        run(scripts, 'validate_atlas.py', work / 'spritesheet.png', '--require-v2',
            '--json-out', reports / 'validation-extended.json')
        run(scripts, 'measure_direction_continuity.py', work / 'spritesheet.png',
            '--json-out', reports / 'look-continuity.json')
        # All exported frames are cropped from the exact cleaned atlas bytes.
        frame_records = []
        with Image.open(work / 'spritesheet.png') as opened:
            atlas = opened.convert('RGBA')
        for row, (state, count) in enumerate({**STATES, 'look': 16}.items()):
            (frames / state).mkdir(exist_ok=True)
            for index in range(count):
                r = 9 + index // 8 if state == 'look' else row
                col = index % 8
                image = atlas.crop((col * 192, r * 208, (col + 1) * 192, (r + 1) * 208))
                relative = f'逐帧PNG/{state}/{index:02d}.png'
                image.save(work / relative)
                record = dict(state=state, index=index, row=r, column=col,
                              file=relative, sha256=sha(work / relative))
                if state == 'look':
                    record['angle_degrees'] = index * 22.5
                frame_records.append(record)
        run(scripts, 'inspect_frames.py', '--frames-root', frames,
            '--json-out', reports / 'review.json', '--require-components')
        run(scripts, 'render_animation_previews.py', '--frames-root', frames, '--output-dir', previews)
        by_state = {}
        for state, count in {**STATES, 'look': 16}.items():
            by_state[state] = []
            for index in range(count):
                with Image.open(frames / state / f'{index:02d}.png') as image:
                    by_state[state].append(image.convert('RGBA'))
        save_gif(previews / 'all-states.gif', [im for s in STATES for im in by_state[s]], 140)
        save_gif(previews / 'look-loop.gif', by_state['look'], 180)
        save_gif(previews / 'idle-hover-idle.gif',
                 by_state['idle'] + by_state['jumping'] + by_state['idle'], 150)
        run(scripts, 'make_contact_sheet.py', work / 'spritesheet.png',
            '--output', work / 'contact-sheet.png', '--scale', '.5')
        run(scripts, 'make_direction_qa_sheet.py', work / 'spritesheet.png',
            '--output', work / 'directions.png')
        manifest = read(folder / '素材清单.json')
        manifest['atlas']['sha256'] = sha(work / 'spritesheet.png')
        manifest['frames'] = frame_records
        manifest['build_record'] = '验证/构建记录.json'
        write(work / '素材清单.json', manifest)
        # Use stable project-relative report paths rather than ephemeral temp paths.
        def relative_paths(value):
            if isinstance(value, str):
                return value.replace(str(work), '.').replace(str(folder), '.')
            if isinstance(value, list):
                return [relative_paths(v) for v in value]
            if isinstance(value, dict):
                return {k: relative_paths(v) for k, v in value.items()}
            return value
        for path in reports.glob('*.json'):
            write(path, relative_paths(read(path)))
        write(reports / '素材完整性.json', dict(
            scope='source_derived_local_build', atlas='spritesheet.png',
            sha256=sha(work / 'spritesheet.png'), width=1536, height=2288,
            frame_count=73, cell_width=192, cell_height=208,
            all_frame_pixels_match_atlas=True, local_atlas_validation_ok=True,
            official_pet_validation_run=False,
            notes='由当前创作素材构建；通过本地结构检查，未执行线上预检或完整画面语义验收。'))
        # Check the outputs before replacing current project deliverables.
        expected = {**STATES, 'all-states': 57, 'look-loop': 16, 'idle-hover-idle': 17}
        for name, count in expected.items():
            with Image.open(previews / f'{name}.gif') as image:
                assert image.n_frames == count and image.size == (192, 208)
                assert image.info.get('loop') == 0
        assert inputs == [{'file': f'创作素材/{f}', 'sha256': sha(source / f)} for f in source_files]
        (frames / 'frames-manifest.json').unlink()
        generated = sorted(p for p in work.rglob('*') if p.is_file() and (
            p.parent == work and p.name in ('spritesheet.png', 'contact-sheet.png', 'directions.png', '素材清单.json')
            or frames in p.parents or previews in p.parents or reports in p.parents))
        outputs = [{'file': p.relative_to(work).as_posix(), 'sha256': sha(p)} for p in generated]
        script_names = ['extract_strip_frames.py', 'inspect_frames.py', 'compose_atlas.py',
                        'assemble_extended_atlas.py', 'despill_chroma_edges.py', 'validate_atlas.py',
                        'measure_direction_continuity.py', 'render_animation_previews.py',
                        'make_contact_sheet.py', 'make_direction_qa_sheet.py']
        write(reports / '构建记录.json', dict(
            dependency_order=['创作素材/三视图.jpg', '创作素材/基础造型.png',
                              '创作素材/动作与方向源图', '精灵图、逐帧图、动作与方向总览', '预览/'],
            note='三视图到基础造型、基础造型到动作源图为已完成的美术步骤；脚本从现有动作源图确定性构建派生文件，不重新生成角色。',
            source_files=inputs, generated_files=outputs, builder_sha256=sha(Path(__file__)),
            bundled_tools=[{'file': n, 'sha256': sha(scripts / n)} for n in script_names]))
        for path in [*generated, reports / '构建记录.json']:
            destination = folder / path.relative_to(work)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        # These old hand-reviewed reports describe different artwork; Git retains them.
        for name in ('pet-quality.json', 'direction-semantics.json'):
            (folder / '验证' / name).unlink(missing_ok=True)
        print(f'{outfit}: 73 source-derived frames, 12 GIFs, atlas and QA sheets built.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outfits', nargs='*', default=['常服', '冬装'])
    parser.add_argument('--skill-scripts', type=Path)
    args = parser.parse_args()
    scripts = args.skill_scripts
    if scripts is None:
        candidates = sorted((Path.home() / '.codex/plugins/cache/openai-curated-remote/work-pets').glob('*/skills/create-pet/scripts'))
        if not candidates:
            parser.error('Pass --skill-scripts pointing to the installed create-pet scripts directory.')
        scripts = candidates[-1]
    for outfit in args.outfits:
        if outfit not in ('常服', '冬装'):
            parser.error('Only 常服 and 冬装 are supported.')
        build(outfit, scripts.resolve())


if __name__ == '__main__':
    main()
