"""제출에 필요한 파일, 파이썬 문법, 실제 PNG 포함 여부를 확인한다."""

import argparse
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    'PRD.md', 'README.md', 'requirements.txt',
    'main.py', 'boy.py', 'grass.py', 'settings.py',
    'assets/animation_sheet.png', 'assets/grass.png',
    'docs/state_diagram.mmd', 'docs/state_diagram.png', 'docs/VALIDATION.md',
    'docs/idle.png', 'docs/auto_run.png', 'docs/run.png', 'docs/sleep.png',
    'tests/test_controller.py', 'tests/test_game_loop.py',
    'tools/render_smoke.py', 'tools/generate_state_diagram.ps1',
)


def check_submission(root):
    errors = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f'누락되었거나 빈 파일: {relative}')
            continue
        if path.suffix == '.py':
            try:
                compile(path.read_text(encoding='utf-8'), relative, 'exec')
            except (SyntaxError, UnicodeError) as error:
                errors.append(f'파이썬 문법 또는 인코딩 오류: {relative}: {error}')
        elif path.suffix == '.png':
            header = path.read_bytes()[:24]
            if len(header) < 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
                errors.append(f'실제 PNG 이미지가 아님: {relative}')
                continue
            width, height = struct.unpack('>II', header[16:24])
            if width <= 0 or height <= 0:
                errors.append(f'이미지 크기가 잘못됨: {relative}')
            if relative == 'assets/animation_sheet.png' and (width < 800 or height < 400):
                errors.append('소년 애니메이션 시트에 필요한 프레임 영역이 부족함')
            if relative in ('docs/idle.png', 'docs/auto_run.png', 'docs/run.png', 'docs/sleep.png'):
                if (width, height) != (800, 600):
                    errors.append(f'실행 예시 이미지의 화면 크기가 800 x 600이 아님: {relative}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='확인할 프로젝트 폴더')
    args = parser.parse_args()
    errors = check_submission(args.root.resolve())
    if errors:
        for error in errors:
            print(f'실패: {error}')
        return 1
    print(f'통과: 제출 필수 파일 {len(REQUIRED_FILES)}개, 파이썬 문법, PNG 이미지 확인')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
