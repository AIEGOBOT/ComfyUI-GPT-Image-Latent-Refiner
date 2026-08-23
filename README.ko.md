# ComfyUI GPT Image Latent Refiner

[English](README.md) | **한국어**

`GPT Image Latent Refiner`는 GPT Image 계열 이미지에서 반복적으로 나타나는
점 노이즈, 점묘, 때가 낀 듯한 질감과 타일 형태의 미세 텍스처를 줄이면서 원본
구도를 최대한 유지하기 위한 ComfyUI 후처리 노드입니다. 세 종류의 VAE 잠재공간
중 하나에서 작은 residual network를 실행합니다.

## 출처와 프로젝트 범위

이 프로젝트는 Larryvrh의
[GPT Image 2 Artifact Cleaner](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner)와
그 프로젝트가 사용한 latent-residual 방식에서 아이디어를 얻었습니다. 이 저장소의
refiner 체크포인트는 별도로 수집하고 정리한 아티팩트/클린 이미지 75쌍을 사용해
독립적으로 학습했습니다. 원본 프로젝트의 체크포인트는 이곳에 포함하거나 재배포하지
않습니다.

원본 프로젝트는 FLUX.2-VAE 파이프라인을 사용합니다. 이 프로젝트는 해당 접근법을
ComfyUI 네이티브 노드로 구성하고 Qwen Image, FLUX.2, SDXL VAE에 맞춰 각각 학습한
세 가지 프로필을 제공합니다. 원본 소스에는 별도의
[PolyForm Noncommercial License 1.0.0](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner/blob/main/LICENSE)이
적용됩니다.

## 프로필

| 프로필 | 상태 | 용도와 특성 |
|---|---|---|
| `qwen` | 권장 기본값 | 노이즈 제거와 원본 보존의 균형이 가장 좋았던 프로필 |
| `flux2` | 안정적인 대안 | 정리 효과는 비교적 약하지만 원본 디테일을 더 많이 보존 |
| `sdxl` | 실사 인물 대안 | 재구성 변화가 강하지만 실사 인물 사진에서는 Qwen이나 FLUX.2보다 효과적일 수 있음 |

`strength`는 `0.0`부터 `2.0`까지 조절할 수 있습니다. `1.0`은 학습된 보정량을
그대로 적용하고, `0.0`은 실제 우회 동작이며, `1.0`을 넘으면 학습된 residual
보정량을 확대합니다.

## 로컬 설치

이 저장소를 `ComfyUI/custom_nodes` 아래에 복제하거나 연결하고, ComfyUI의 Python
환경에 의존성을 설치한 뒤 ComfyUI를 다시 시작합니다.

```powershell
& '<ComfyUI>\venv\Scripts\python.exe' -m pip install -r requirements.txt
```

이 프로젝트는 체크포인트와 VAE 가중치를 저장소에 포함하지 않습니다. 파일을 다음
경로에 설치해야 합니다.

```text
ComfyUI/models/gpt_image_latent_refiner/qwen/model.pt
ComfyUI/models/gpt_image_latent_refiner/flux2/model.pt
ComfyUI/models/gpt_image_latent_refiner/sdxl/model.pt

ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/diffusion_pytorch_model.safetensors
ComfyUI/models/vae/GPT-Image-Latent-Refiner/flux2/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/flux2/diffusion_pytorch_model.safetensors
ComfyUI/models/vae/GPT-Image-Latent-Refiner/sdxl/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/sdxl/diffusion_pytorch_model.safetensors
```

노드는 선택한 프로필, latent channel 수, 체크포인트 metadata와 VAE 파일이 서로
맞는지 확인합니다. 호환되지 않는 파일을 조용히 섞어서 실행하지 않습니다.

## 노드 정보

- 노드 ID: `indii.GPTImageLatentRefiner`
- 표시 이름: `GPT Image Latent Refiner`
- 카테고리: `GPT Image/refinement`
- 입력: `image`, `profile`, `strength`, `device`, `tile_vae`
- 출력: `image`

처음에는 `qwen`, `strength=1.0`, `device=auto`, `tile_vae=true`로 시작하세요.
16GB GPU에서는 큰 이미지를 한 번에 한 장씩 처리하는 것을 권장합니다.

## 권장 SeedVR2 워크플로우

리파이너를 단독으로 사용할 수도 있지만, 제작자 테스트에서는 SeedVR2 앞에 배치했을
때 효과가 가장 뚜렷했습니다. 반복 점무늬와 불안정한 미세 질감을 먼저 정리해
SeedVR2가 이를 이미지 디테일로 재구성하거나 확대할 가능성을 줄입니다.

저장소에 포함된
[GPT Image Refiner + SeedVR2 워크플로우](example_workflows/GPT_Image_Refiner_SeedVR2.json)는
다음 순서로 처리합니다.

```text
입력 -> GPT Image Latent Refiner -> Area 0.5배 축소 -> SeedVR2 복원
     -> Wavelet 색상 보정 -> CAS -> 최종 출력
```

Bicubic 노드가 목표 픽셀 해상도를 먼저 정하고, SeedVR2가 그 크기에서 이미지를
재구성하고 복원합니다.

`0.5배` 축소는 의도적으로 넣은 단계지만 필수는 아닙니다. Area 축소가 불안정한
고주파 패턴을 평균화한 뒤 SeedVR2가 이미지를 다시 구성하므로 점 노이즈나 격자
질감이 디테일로 보존될 가능성을 줄일 수 있습니다. 반대로 실제 미세 디테일이나 작은
글자도 사라질 수 있으므로 원본 보존이 더 중요하면 배율을 `1.0`으로 바꾸거나 해당
노드를 우회하세요.

### 커스텀 노드 의존성

이 예제의 SeedVR2 부분은
[ComfyUI 네이티브 노드](https://docs.comfy.org/tutorials/utility/seedvr2)를
사용합니다. 해당 노드가 보이지 않으면 ComfyUI를 업데이트하세요. 배포된 그래프에는
다음 노드 팩도 사용됩니다.

| 노드 팩 | 사용 노드 | 용도 |
|---|---|---|
| [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials) | `ImageCASharpening+` | 마지막 CAS 선명도 보정 |
| [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use) | `easy cleanGpuUsed`, `easy clearCacheAll` | 무거운 단계 사이 GPU 메모리·캐시 정리 |
| [rgthree-comfy](https://github.com/rgthree/rgthree-comfy) | `Image Comparer (rgthree)` | 대화형 결과 비교; 비교 노드를 제거하면 생략 가능 |

### 모델 다운로드

| 파일 | 다운로드 | 설치 위치 |
|---|---|---|
| Qwen 리파이너 `model.pt` | 별도 배포 예정이며 아직 공개 다운로드 없음 | `models/gpt_image_latent_refiner/qwen/model.pt` |
| Qwen Image VAE | [공식 VAE 폴더](https://huggingface.co/Qwen/Qwen-Image/tree/main/vae) | `models/vae/GPT-Image-Latent-Refiner/qwen/` |
| SeedVR2 7B FP16 | [다운로드](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_fp16.safetensors) | `models/diffusion_models/` |
| SeedVR2 7B INT8 ConvRot | [다운로드](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_int8_convrot.safetensors) | `models/diffusion_models/` |
| SeedVR2 VAE FP16 | [다운로드](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/vae/ema_vae_fp16.safetensors) | `models/vae/` |

예제는 리파이너 `qwen` 프로필과 SeedVR2 7B FP16을 사용합니다. 제작자의 비교
테스트를 기준으로 한 모델 선택 안내는 다음과 같습니다.

- **권장:** 이 워크플로우에서 확인한 품질과 아티팩트 억제 효과가 가장 좋은
  SeedVR2 7B FP16
- **VRAM 부족 시 대안:** `seedvr2_7b_int8_convrot.safetensors`. 7B 구조를
  유지하면서 메모리 사용량을 줄일 수 있지만 FP16보다 품질이 낮아질 수 있음
- **주의:** 3B 또는 더 강하게 양자화된 모델은 아티팩트를 다시 드러내거나 강조할
  수 있음. 이는 모든 이미지에 적용되는 절대 기준이 아니라 이 워크플로우에서 관찰한
  경향임

[SeedVR2 워크플로우 상세 설명](docs/SEEDVR2_WORKFLOW.ko.md)에는 각 단계의 역할,
`0.5배` 축소를 생략할 조건과 일반적인 Hires Fix·latent upscale 방식과의 차이를
정리했습니다.

## 저장소 범위

이 저장소에는 ComfyUI 실행 코드, 의존성 metadata와 이동 가능한 예제 워크플로우를
포함합니다. 학습 코드, 데이터셋, 체크포인트, VAE 가중치, 생성 이미지와
비공개 실험 기록은 포함하지 않습니다.

## 제3자 모델

VAE 가중치는 이 저장소와 프로젝트 라이선스에 포함되지 않습니다. 각 공식 출처에서
별도로 받아야 하며 해당 라이선스를 따라야 합니다.

- [Qwen/Qwen-Image](https://huggingface.co/Qwen/Qwen-Image) — Apache License 2.0
- [FLUX.2 autoencoder](https://github.com/black-forest-labs/flux2#flux2-autoencoder) — Apache License 2.0
- [Stable Diffusion XL Base 1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) — CreativeML Open RAIL++-M

전체 출처와 배포 범위는
[THIRD_PARTY_NOTICES.ko.md](THIRD_PARTY_NOTICES.ko.md)에서 확인할 수 있습니다.

## 라이선스

별도 표시가 없는 한 이 저장소의 코드와 이 프로젝트가 공개하는 residual 체크포인트에는
[PolyForm Noncommercial License 1.0.0](LICENSE)이 적용됩니다. 해당 라이선스가
허용하는 비상업적 목적에 한해 사용, 수정 및 공유할 수 있습니다. 상업적 사용 권한은
부여되지 않습니다.

75쌍의 학습 데이터셋과 원본 이미지, 제3자 VAE 가중치 및 원본 GPT Image 2
Artifact Cleaner 체크포인트는 이 저장소에서 배포하지 않습니다. 프로젝트 출처는
[NOTICE.ko.md](NOTICE.ko.md)를 참고하세요.

## 문서 언어 정책

이 프로젝트의 사용자 대상 문서는 영문과 한글을 함께 관리합니다. 법률 문서의 번역이
다를 경우 영문 법률 파일과 각 상위 프로젝트가 공개한 공식 라이선스 원문을 기준으로
합니다.
