# 번들 리파이너 체크포인트

[English](README.md) | **한국어**

이 추론용 체크포인트는 저장소 README에 설명한 자체 구성 75쌍 데이터셋으로 이
프로젝트에서 학습했습니다. 각 파일에는 ComfyUI 노드 실행에 필요한 EMA residual
가중치와 체크포인트 metadata가 들어 있습니다. 학습 optimizer 상태와 중복되는
비 EMA 가중치는 의도적으로 제외했습니다.

공개한 `R_ema` tensor는 배포 전에 해당 학습 체크포인트의 가중치와 완전히 같은지
검증했습니다.

| 프로필 | 파일 | 크기 | SHA-256 |
|---|---|---:|---|
| Qwen | `gpt_image_latent_refiner/qwen/model.pt` | 1,855,465 bytes | `f56de83b01c18c890aa4948393f9029d69596744d711505ac8d581c7dd9af02d` |
| FLUX.2 | `gpt_image_latent_refiner/flux2/model.pt` | 1,929,193 bytes | `32744454f52a32a2e2c8d1a77175f97005b51868ef93c48530eb506b6170d517` |
| SDXL | `gpt_image_latent_refiner/sdxl/model.pt` | 1,800,169 bytes | `5724a88ee116d41bc6dac804eda29fa61d400473079a294585ec771427574142` |

노드는 이 파일을 자동으로 사용합니다. 호환되는 체크포인트를
`ComfyUI/models/gpt_image_latent_refiner/<profile>/model.pt`에 설치하면 외부
파일이 우선되어 번들 체크포인트를 교체할 수 있습니다.

이 프로젝트에서 학습한 체크포인트에는 저장소의
[PolyForm Noncommercial License 1.0.0](../LICENSE)이 적용됩니다. 제3자 VAE
가중치는 포함되지 않으며 각 원 라이선스를 따라야 합니다.
