# GitBook 관리를 위한 Markdown 파일 생성 툴

Jupyter Notebook(`.ipynb`) 파일을 Markdown 파일로 변환하고, GitBook 관리에 적합한 형식으로 저장된다.

## 사용법

### 1. 단일 파일 변환

```python
from markdown_generator.mdconverter_class import MultiNdconverter

file_list = ['04-Model\\06-GoogleGenerativeAI.ipynb'] # 리스트 형식으로 파일 경로
app = MultiNdconverter(filenames=file_list)
app.css_filename = "../css/styles.css" # css 파일 설정
app.post_fix = "-(CHECK)" # option
app.run()
```

### 2. 디렉토리 내 여러 파일 변환


```python
import os
from markdown_generator.mdconverter_class import MultiNdconverter

# 변환할 디렉토리 설정
folder_name = "04-Model"

# 디렉토리 내 모든 `.ipynb` 파일 경로 리스트 생성
file_list = [os.path.join(folder_name, f) for f in os.listdir(folder_name) if f.endswith(".ipynb")]

# 초기화 및 실행
app = MultiNdconverter(filenames=file_list)
app.css_filename = "../css/styles.css"
app.post_fix = "-(CEHCK)" # option
app.run()
```

### 주요 파라미터
- `filenames`: 변환할 Notebook 파일들의 경로 리스트
- `css_filename`: Markdown 파일에 적용할 CSS 파일 경로
- `post_fix`: 저장 파일명의 후위에 추가되는 명칭(기본값 : "-(NEW)")
- `ndconverter_script`: 최종 결과물 보관

### 결과물

결과물은 `docs` 폴더에 생성된다.
