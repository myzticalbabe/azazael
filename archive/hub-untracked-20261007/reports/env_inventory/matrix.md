# Cross-Environment Python Package Matrix

| Environment | Packages |
|---|---:|
| win-main | 637 |
| win-314t | 161 |
| win-313tools | 127 |
| win-interp | 149 |
| ubuntu | 300 |
| kali | 1009 |

- Union of distinct distributions: **1448**
- Present in *every* environment: **64**

## Packages unique to one environment (top 40 each)


### win-main — 276 unique
- absl-py==2.4.0
- accelerate==1.13.0
- adagio==0.2.6
- aifs==0.0.16
- aiofile==3.11.1
- aiomysql==0.3.2
- albucore==0.0.24
- albumentations==2.0.8
- alembic==1.18.4
- appdirs==1.4.4
- astunparse==1.6.3
- authlib==1.7.2
- autopep8==2.3.2
- azure-core==1.41.0
- azure-identity==1.25.3
- beartype==0.22.9
- bitsandbytes==0.49.2
- black==26.5.1
- blis==1.3.3
- burner-redis==0.1.7
- cachetools==7.1.2
- caio==0.9.25
- catalogue==2.0.10
- cloudpathlib==0.24.0
- cobble==0.1.4
- code-review-graph==2.3.3
- confection==1.3.3
- configobj==5.0.9
- courlan==1.4.0
- coverage==7.14.1
- cronsim==2.7
- cxxfilt==0.3.0
- cyclopts==4.13.0
- cymem==2.0.13
- dashscope==1.25.18
- databricks-sdk==0.108.0
- dataclasses-json==0.6.7
- dataproperty==1.1.1
- datasets==4.8.5
- datasketch==1.10.0
- …and 236 more

### win-314t — 5 unique
- cohere==5.1.5
- pdfminer-six==20260107
- pdfplumber==0.11.10
- replicate==1.0.7
- timesfm==3.0.1

### win-313tools — 5 unique
- duckdb==1.5.5
- igraph==1.0.0
- kuzu==0.11.3
- rustworkx==0.18.1
- splink==4.0.17

### win-interp — 0 unique

### ubuntu — 39 unique
- azazael-codex==2.0.0
- azazael-llama-server==1.0.0
- azazael-onnx-runtime==1.0.0
- azazael-pams==1.0.0
- azazael-python-3145t==1.0.0
- azazael-shared==1.0.0
- azazael-tensorflow==1.0.0
- azazael-vision-language==1.0.0
- cuda-bindings==13.3.1
- cuda-pathfinder==1.5.5
- cuda-toolkit==13.0.2
- easyocr==1.7.2
- eve-unleashed==1.1.0
- graphviz==0.21
- impi-rt==2021.17.2
- intel-extension-for-tensorflow==0.0.0.dev1
- jupyter-events==0.12.1
- jupyter-lsp==2.3.1
- jupyter-server==2.19.0
- jupyter-server-terminals==0.5.4
- jupyterlab==4.5.7
- jupyterlab-pygments==0.3.0
- jupyterlab-server==2.28.0
- mutagen==1.47.0
- nbclient==0.10.4
- nbconvert==7.17.1
- notebook-shim==0.2.4
- oneccl==2021.17.2
- oneccl-devel==2021.17.2
- pandocfilters==1.5.1
- python-json-logger==4.1.0
- python-louvain==0.16
- rfc3987-syntax==1.1.0
- screeninfo==0.8.1
- terminado==0.18.1
- timm==1.0.28
- torchvision==0.28.0
- uri-template==1.3.0
- worm-manifest==0.1.0

### kali — 712 unique
- aadict==0.2.3
- above==2.8.1
- acstore==20240407
- adblockparser==0.7
- aesedb==0.1.4
- aiocmd==0.1.2
- aioconsole==0.8.2
- aioftp==0.27.2
- aiohttp-apispec==3.0.0b2
- aiohttp-jinja2==1.6
- aiohttp-security==0.5.0
- aiohttp-session==2.12.1
- aiomultiprocess==0.9.0
- aioquic==1.2.0
- aiosmb==0.4.4
- aiosqlite==0.22.1
- aiowinreg==0.0.7
- ajpy==0.0.5
- alabaster==1.0.0
- aniso8601==10.0.1
- apispec==6.10.0
- arc4==0.4.0
- arjun==2.2.7
- arpy==1.1.1
- artifacts==20230928
- asciitree==0.3.3
- asn1crypto==1.5.1
- asn1tools==0.166.0
- asset==0.6.13
- astroid==4.1.1
- asyauth==0.0.20
- asyncssh==2.23.0
- asysocks==0.2.12
- atomic-operator==0.9.1
- atomic-operator-runner==0.2.1
- awscli==2.31.35
- awscrt==1.0.0.dev0
- backports-zstd==1.5.0
- bidict==0.23.1
- binwalk==2.4.3
- …and 672 more


## Runtime-critical package matrix

| package | win-main | win-314t | win-313tools | win-interp | ubuntu | kali |
|---|---|---|---|---|---|---|
| numpy | 2.5.3 | 2.4.6 | 2.5.2 | 2.5.1 | 2.4.6 | 2.5.3 |
| scipy | 1.18.1 | 1.18.0 | 1.18.1 | — | 1.17.1 | 1.16.3 |
| torch | 2.14.0+cpu | 2.14.0 | — | — | 2.12.0 | — |
| torchvision | — | — | — | — | 0.28.0 | — |
| transformers | 5.17.0 | — | — | — | 5.9.0 | — |
| tokenizers | 0.23.2 | 0.23.2 | 0.23.2 | 0.23.1 | 0.22.2 | — |
| safetensors | 0.9.0rc0 | — | — | — | 0.7.0 | — |
| accelerate | 1.13.0 | — | — | — | — | — |
| peft | 0.19.1 | — | — | — | — | — |
| trl | 1.4.0 | — | — | — | — | — |
| datasets | 4.8.5 | — | — | — | — | — |
| sentence-transformers | 5.5.1 | — | — | — | 6.0.0 | — |
| onnxruntime | 1.30.0 | — | 1.29.0 | — | — | — |
| onnx | 1.21.0 | — | — | — | — | — |
| openvino | 2026.2.0 | — | — | — | 2026.2.0 | — |
| llama-cpp-python | 0.3.23 | — | — | — | 0.3.23 | — |
| gymnasium | 1.2.3 | — | — | — | — | — |
| stable-baselines3 | 2.9.0 | — | — | — | — | — |
| sb3-contrib | 2.9.0 | — | — | — | — | — |
| scikit-learn | 1.9.1 | 1.9.0 | 1.9.0 | — | 1.8.0 | 1.8.0 |
| pandas | 3.0.5 | 3.0.3 | 3.0.5 | — | 2.3.3 | 2.3.3 |
| matplotlib | 3.11.2 | 3.11.2 | — | 3.11.0 | 3.10.9 | 3.11.1 |
| networkx | 3.6.1 | — | 3.6.1 | — | 2.8.8 | 2.8.8 |
| igraph | — | — | 1.0.0 | — | — | — |
| python-louvain | — | — | — | — | 0.16 | — |
| fastapi | 0.136.1 | — | — | — | 0.136.3 | 0.138.1 |
| uvicorn | 0.47.0 | — | 0.52.4 | — | — | 0.52.1 |
| flask | 3.1.3 | — | — | — | 3.1.3 | 3.1.3 |
| aiohttp | 3.13.5 | 3.14.3 | 3.14.3 | 3.14.1 | 3.14.3 | 3.14.3 |
| httpx | 0.28.1 | 0.28.1 | 0.28.1 | 0.28.1 | 0.28.1 | 0.28.1 |
| openai | 3.16.2 | 3.16.0 | 3.8.0 | 2.44.0 | 2.41.1 | 2.21.0 |
| anthropic | 0.37.1 | 1.6.0 | — | 0.116.0 | 1.0.0 | — |
| litellm | 1.83.0 | 1.83.0 | — | 1.83.0 | 1.83.7 | — |
| google-generativeai | 0.7.2 | — | — | 0.8.6 | 0.8.6 | — |
| pydantic | 2.13.4 | 2.13.5 | 2.13.5 | 2.13.4 | 2.13.4 | 2.13.4 |
| rich | 15.0.0 | 15.0.0 | 15.0.0 | 15.0.0 | 15.0.0 | 13.9.4 |
| psutil | 7.2.2 | 7.2.2 | 7.2.2 | 7.2.2 | 7.2.2 | 7.2.2 |
| pillow | 12.3.0 | 12.3.0 | — | 12.3.0 | 12.3.0 | 12.3.0 |
| nuitka | 4.1.2 | — | — | — | 4.1.3 | 4.1.2 |
| pytest | 9.0.3 | 9.1.1 | — | — | 9.0.3 | 9.1.0 |
| mypy | 2.1.0 | — | — | — | 2.2.0 | 2.1.0 |
| ruff | 0.15.17 | — | — | — | — | — |
| hypothesis | — | 6.155.7 | — | — | 6.155.7 | 6.155.6 |
| chromadb | 1.5.9 | — | 1.5.9 | — | — | — |
| faiss-cpu | 1.12.0 | — | — | — | — | — |
| tiktoken | 0.7.0 | 0.14.0 | — | 0.13.0 | 0.14.0 | — |
| pyarrow | 25.0.1 | 24.0.0 | 25.0.1 | — | — | — |
| ray | 2.58.0 | — | — | — | — | — |
| dask | — | — | — | — | — | 2024.12.1+dfsg |
| sqlalchemy | 2.0.49 | — | — | — | — | 2.0.51 |
| alembic | 1.18.4 | — | — | — | — | — |
| redis | 7.4.0 | — | — | — | — | 6.4.0 |
| kuzu | — | — | 0.11.3 | — | — | — |
| graphiti-core | — | 0.30.1 | 0.30.1 | — | — | — |
| neo4j | — | 6.3.0 | 6.3.0 | — | — | 5.2.dev0 |
| rustworkx | — | — | 0.18.1 | — | — | — |
| pyvis | 0.3.2 | 0.3.2 | 0.3.2 | — | 0.3.2 | 0.3.2 |
| plotly | 7.0.0 | — | — | — | — | 5.20.0 |
| streamlit | 1.57.0 | — | — | — | — | — |

**Absent from every Python environment:** llama-cpp-python-cuda, community, soundfile, librosa, sentencepiece, polars, dash, gradio
