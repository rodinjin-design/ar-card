# AR Card

세로형 실물 크기(54 × 85.6mm) 카드를 3D·AR로 보는 데모 페이지.

- **손 위에 올리기**: 카메라로 손바닥을 인식해 카드를 손 위에 띄움 (MediaPipe Hand Landmarker + three.js)
- **책상 위에 놓기**: Android Scene Viewer / iOS Quick Look AR (model-viewer)
- 카드: `models/snack.glb`, `models/travel.glb` (디자인 © jean.on)

카드 추가·교체:
```
python3 build_card.py 앞면.png 뒷면.png models/새카드.glb --portrait
```
그리고 `index.html`의 `CARDS`에 항목을 추가한다.
