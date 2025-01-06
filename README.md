# gitbook 관리를 위한 markdown 파일 생성 툴

## 사용법

```bash
python mdconverter.py --filename <notebook-file-path>
```

**예시**

```bash
python mdconverter.py --filename sample/05-GoogleGenerativeAI.ipynb
```

개발 중...
```python

from mdconverter.mdconverter_class import Mdconverter
app = Mdconverter()
app.filename = "sample/05-GoogleGenerativeAI.ipynb"
app.output_filename = 'sample/New-05-GoogleGenerativeAI.md'
app.css_filename = "css/styles.css"

app.run()
```
