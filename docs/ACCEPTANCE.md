# 채점 항목별 확인 방법

| 과제 조건 | 구현 위치 | 실행 시 확인 | 관련 검증 |
| --- | --- | --- | --- |
| Idle에서 A를 누르면 자동 무적 런 | `Boy.handle_event`, `AutoRun.enter` | 게임 시작 직후 A를 누르고 뗀다. 입력 없이 이동해야 한다. | `test_a_starts_auto_run_and_release_does_not_stop_it` |
| 5초가 지나면 Idle 복귀 | `AUTO_RUN`의 `tick` 전환, `AutoRun.update` | 자동 이동 시작 5초 후 기본 크기로 멈춰야 한다. | `test_auto_run_expires_at_five_seconds_not_before`, `test_timeout_frame_includes_the_full_five_seconds_of_movement` |
| 속도가 빨라지고 크기가 커짐 | `settings.py`, `AutoRun.enter`, `draw_running_sprite` | 일반 Run은 200픽셀/초·100×100, AutoRun은 400픽셀/초·150×150이다. | `test_auto_run_is_twice_as_fast_as_run`, `test_enlargement_preserves_the_bottom_of_the_sprite` |
| 좌우 끝에서 자동 방향 전환 | `AutoRun.update` | 양 끝에서 확대된 소년 전체가 화면 안에 머물며 반사되어야 한다. | 좌우 경계·정확한 경계 도착·다중 반사 검증 |
| 방향키로 취소 후 원래 Run | `start_running` 전환, `AutoRun.exit` | AutoRun 중 방향키를 누르면 그 방향의 기본 속도·크기로 움직여야 한다. | `test_either_arrow_cancels_auto_run_into_normal_run` |
| 별도의 AutoRun 상태 클래스 | `boy.py`의 `class AutoRun` | 진입·갱신·종료·그리기를 클래스에서 처리한다. | `test_auto_run_has_a_dedicated_state_class` |
| 상태 다이어그램 이미지 제출 | `docs/state_diagram.png`, `docs/state_diagram.mmd` | 저장소 README에서 한국어 상태도 이미지를 확인한다. | `tools/check_submission.py` |

## 제출 전 확인

1. `python tools/check_submission.py`로 코드·이미지·문서 누락 여부를 점검한다.
2. `python -m unittest discover -s tests -v`로 32개 검증을 실행한다.
3. `python tools/render_smoke.py`로 실제 이미지 렌더링을 확인한다.
4. GitHub 저장소의 공개 여부, 업로드된 소스·이미지, 한국어 커밋 기록을 확인한다.
5. e-Class에 `.git`으로 끝나는 저장소 주소를 학생 본인이 제출한다.

```text
https://github.com/junhwijunhwi/2DGP-2023180015-Drill11-AutoRun.git
```
