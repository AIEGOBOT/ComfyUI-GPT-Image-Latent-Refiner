# 프로젝트 고지 — 비공식 한글 번역

법적 고지의 기준은 영문 [NOTICE](NOTICE)와 [LICENSE](LICENSE)입니다.

GPT Image Latent Refiner
Copyright (c) 2026 AIEGOBOT

이 프로젝트는 다음 프로젝트에서 설명하고 구현한 latent-residual 아티팩트 정리
방식과 compact residual network 설계를 응용했습니다.

- GPT Image 2 Artifact Cleaner
- Copyright (c) 2026 Larryvrh
- https://github.com/Larryvrh/gpt-image-2-artifact-cleaner
- PolyForm Noncommercial License 1.0.0
- https://polyformproject.org/licenses/noncommercial/1.0.0

원본 프로젝트의 체크포인트는 이 저장소에 포함하거나 재배포하지 않습니다. GPT Image
Latent Refiner의 residual 체크포인트는 별도로 수집한 아티팩트/클린 이미지 75쌍을
사용해 무작위 초기화 상태부터 따로 학습했습니다. 이 프로젝트는 ComfyUI 네이티브
노드와 각각 별도로 학습한 Qwen Image, FLUX.2, SDXL VAE 프로필을 추가합니다.

제3자 VAE 가중치와 학습 데이터셋은 이 저장소에 포함하지 않습니다. 출처와 라이선스
범위는 [THIRD_PARTY_NOTICES.ko.md](THIRD_PARTY_NOTICES.ko.md)를 참고하세요.
