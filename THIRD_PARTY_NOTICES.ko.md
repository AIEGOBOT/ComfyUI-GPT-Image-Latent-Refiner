# 제3자 구성요소 고지

[English](THIRD_PARTY_NOTICES.md) | **한국어**

제3자 체크포인트와 VAE 가중치는 이 저장소에 포함하지 않습니다. 각 구성요소에는
해당 프로젝트의 라이선스가 별도로 적용되며 공식 출처에서 직접 받아야 합니다.

## 아이디어와 구현 참고 출처

- 프로젝트: [GPT Image 2 Artifact Cleaner](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner)
- 작성자 및 저작권: Larryvrh, Copyright (c) 2026
- 참고 범위: latent-residual 아티팩트 정리 방식과 compact residual network 설계
- 라이선스: [PolyForm Noncommercial License 1.0.0](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner/blob/main/LICENSE)
- 포함 여부: 원본 프로젝트의 체크포인트는 포함하거나 재배포하지 않음

## VAE 의존성

| 프로필 | 상위 모델 | 라이선스 | 저장소 포함 여부 |
|---|---|---|---|
| Qwen Image | [Qwen/Qwen-Image](https://huggingface.co/Qwen/Qwen-Image) | Apache License 2.0 | 포함하지 않음 |
| FLUX.2 | [FLUX.2 autoencoder](https://github.com/black-forest-labs/flux2#flux2-autoencoder) | Apache License 2.0 | 포함하지 않음 |
| SDXL | [stabilityai/stable-diffusion-xl-base-1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) | CreativeML Open RAIL++-M | 포함하지 않음 |

위 라이선스는 각각의 제3자 구성요소에 적용됩니다. GPT Image Latent Refiner가
독자적으로 작성한 코드와 residual 체크포인트에 적용되는 라이선스가 아닙니다.
