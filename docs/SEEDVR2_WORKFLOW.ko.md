# GPT Image Latent Refiner + SeedVR2 워크플로우

[English](SEEDVR2_WORKFLOW.md) | **한국어**

이 문서는 저장소에 포함된
[예제 워크플로우](../example_workflows/GPT_Image_Refiner_SeedVR2.json)의 설계 이유를
설명합니다. 품질 권장은 정식 벤치마크가 아니라 제작자의 비교 테스트를 기준으로
하므로 중요한 이미지는 저장 전에 비교 노드로 직접 확인하세요.

## 전체 처리 흐름

```text
입력 이미지
  -> GPT Image Latent Refiner (Qwen 프로필)
  -> 선택형 Area 0.5배 축소
  -> 최장변 1920px bicubic 크기 조정
  -> ComfyUI 네이티브 SeedVR2 전처리와 복원
  -> Wavelet 색상 보정
  -> CAS 선명도 보정
  -> 최종 출력
```

### 1. Latent 정제

Qwen 리파이너가 생성형 복원 전에 반복 점무늬, 점묘, 때가 낀 듯한 질감과 불안정한
미세 패턴을 줄입니다. 단독 결과는 변화가 약해 보일 수 있습니다. 이 그래프에서의
핵심 역할은 SeedVR2가 문제 아티팩트를 정상 디테일로 판단해 다시 구성하고 선명하게
만드는 현상을 줄이는 것입니다.

### 2. 선택형 Area 0.5배 축소

Area 축소는 이웃 픽셀을 합쳐 평균화합니다. 한두 픽셀 크기의 미세 패턴은 약해지거나
서로 섞입니다. 즉, 일부 정보를 의도적으로 버리고 SeedVR2가 더 일관된 질감을 다시
구성할 공간을 만드는 단계입니다.

기대할 수 있는 장점:

- 복원 전에 불안정한 고주파 점무늬와 격자 패턴을 약화함
- 오염된 기존 디테일이 그대로 커지는 현상을 줄임
- 복원 모델이 다시 구성할 구조를 더 단순하고 일관되게 만듦
- 리파이너 단계와 최종 출력의 차이를 더 뚜렷하게 만들 수 있음

이 단계는 필수가 아닙니다. 다음 조건에서는 `ImageScaleBy`를 `1.0`으로 바꾸거나
노드를 우회하는 편이 좋습니다.

- 원본이 이미 깨끗하거나 해상도가 낮은 경우
- 작은 글자, UI 요소, 제품 라벨, 선화 또는 직물 무늬가 정확해야 하는 경우
- 인물의 정체성과 관련된 미세한 얼굴 특징을 보존해야 하는 경우
- 불필요한 질감보다 실제 디테일이 더 많이 사라지는 경우

`0.5배` 축소는 주된 VRAM 절약 옵션이 아닙니다. 다음 노드가 최장변을 1920px로
다시 맞추며, 실제 SeedVR2 처리 해상도가 메모리 사용량에 더 큰 영향을 줍니다.

### 3. 목표 크기 조정과 SeedVR2 복원

Bicubic 크기 조정으로 작업 해상도를 먼저 확정한 뒤 ComfyUI 네이티브 SeedVR2
전처리를 적용합니다. SeedVR2는 복원 목적의 생성 처리를 한 단계로 수행합니다.
단순 보간 필터와 달리 그럴듯한 윤곽과 질감을 다시 만들 수 있지만, 디테일을 새로
추측하거나 다르게 해석할 가능성도 있습니다.

정확히는 bicubic 노드가 픽셀 해상도를 바꾸고 SeedVR2는 그 목표 크기에서 이미지를
복원합니다. 따라서 전체 과정은 SeedVR2가 고정 배율로 이미지를 단순 확대하는
방식보다는 **축소-크기 조정-복원 파이프라인**으로 설명하는 편이 정확합니다.

이 워크플로우는 `seedvr2_7b_fp16.safetensors`를 사용합니다. 제작자 테스트에서
아티팩트 억제와 최종 질감이 가장 좋았습니다. FP16으로 메모리 부담이 지나치게 크면
`seedvr2_7b_int8_convrot.safetensors`를 사용하세요. 3B와 더 강하게 양자화된
모델은 현재 테스트에서 아티팩트를 다시 드러내거나 강조하는 경우가 더 많았습니다.
이는 SeedVR2 모델 전체에 대한 절대 순위가 아니라 이 워크플로우에서 관찰한 결과입니다.

### 4. 색상 보정과 CAS

Wavelet 색상 보정은 크기를 맞춘 입력 색상을 참조해 복원 과정의 색상 이동을 줄입니다.
CAS는 리파이너, 크기 조정과 복원을 거치며 약해질 수 있는 가장자리의 국부 대비를
마지막에 절제해서 보완합니다. CAS는 의미 있는 새 디테일을 만드는 노드가 아니며,
강도를 과도하게 높이면 남은 노이즈나 halo가 다시 보일 수 있습니다.

## 일반적인 Hires Fix와의 차이

일반적인 Hires Fix 또는 latent upscale은 생성된 이미지나 latent를 키운 뒤 diffusion
sampling을 한 번 더 수행합니다. 프롬프트를 기반으로 디테일을 확장할 때는 유용하지만,
아티팩트 제거 목적에서는 denoise 강도에 따른 절충이 까다롭습니다.

| | 일반적인 Hires Fix / latent upscale | 이 워크플로우 |
|---|---|---|
| 주목적 | 더 큰 해상도에서 생성을 이어감 | 아티팩트를 정리한 뒤 이미지를 복원함 |
| 주요 제어 | 프롬프트, sampler, step, denoise 강도 | 리파이너 프로필, 선택형 축소, 복원 모델 |
| 재구성 강도가 낮을 때 | 기존 아티팩트와 흐림이 남을 수 있음 | 복원 전에 문제 질감을 리파이너가 먼저 줄임 |
| 재구성 강도가 높을 때 | 얼굴, 정체성, 글자, 구도와 형태가 달라질 수 있음 | SeedVR2도 디테일을 바꿀 수 있지만 복원 모델로 사용함 |
| 디테일의 출처 | 생성 모델의 두 번째 sampling | 처리된 이미지를 조건으로 한 SeedVR2 복원 |

Hires Fix 자체가 열등한 방식은 아닙니다. 해결하려는 문제가 다릅니다. GPT Image의
반복 질감 아티팩트를 정리할 때 일반 생성 모델의 두 번째 sampling은 denoise가 낮으면
문제까지 확대하고, 높으면 이미지를 다시 구성할 수 있습니다. 리파이너와 SeedVR2의
조합은 정리와 재구성을 분리해 이 절충을 더 쉽게 제어합니다.

## 필요한 노드

이 그래프의 SeedVR2 전처리, conditioning과 후처리는 ComfyUI 네이티브 노드입니다.
[공식 네이티브 SeedVR2 안내](https://docs.comfy.org/tutorials/utility/seedvr2)도
참고할 수 있습니다. 정확히 같은 예제를 실행하려면 다음 외부 노드 팩도 필요합니다.

| 노드 팩 | 역할 | 현재 그래프에서 필요 여부 |
|---|---|---|
| [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials) | CAS 선명도 보정 | 필요 |
| [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use) | GPU 메모리·캐시 정리 | 필요 |
| [rgthree-comfy](https://github.com/rgthree/rgthree-comfy) | 이미지 비교 | 비교 노드를 제거하면 생략 가능 |

## 모델과 설치 경로

| 모델 | 링크 | 설치 위치 |
|---|---|---|
| Qwen 리파이너 체크포인트 | 아직 공개 배포하지 않음 | `ComfyUI/models/gpt_image_latent_refiner/qwen/model.pt` |
| Qwen Image VAE | [공식 파일](https://huggingface.co/Qwen/Qwen-Image/tree/main/vae) | `ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/` |
| SeedVR2 7B FP16 | [다운로드](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_fp16.safetensors) | `ComfyUI/models/diffusion_models/` |
| SeedVR2 7B INT8 ConvRot | [다운로드](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_int8_convrot.safetensors) | `ComfyUI/models/diffusion_models/` |
| SeedVR2 VAE FP16 | [다운로드](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/vae/ema_vae_fp16.safetensors) | `ComfyUI/models/vae/` |

Qwen VAE 설치 폴더에는 `config.json`과
`diffusion_pytorch_model.safetensors`가 모두 있어야 합니다.

## 한계와 주의사항

- SeedVR2는 무손실 복원이 아니라 생성형 복원입니다. 원본에서 불분명한 디테일을
  새로 만들거나 다르게 바꿀 수 있습니다.
- SeedVR2 공식 프로젝트도 손상이 적은 입력에서는 디테일을 과도하게 만들거나
  지나치게 선명해질 수 있다고 안내합니다. 자세한 내용은
  [SeedVR2 공식 저장소](https://github.com/ByteDance-Seed/SeedVR)를 참고하세요.
- `0.5배` 축소 단계에서 실제 미세 디테일이 복원 전에 영구적으로 사라질 수 있습니다.
- CAS 강도가 높으면 남아 있는 노이즈도 다시 선명하게 만들 수 있습니다.
- 특히 7B FP16은 먼저 큰 이미지 한 장씩 처리하세요.
