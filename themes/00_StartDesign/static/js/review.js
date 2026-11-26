        const canvas = document.getElementById('review-canvas');
        const ctx = canvas.getContext('2d');
        const tools = document.getElementById('review-tools');
        const toggleBtn = document.getElementById('reviewToggleBtn');
        const eraserBtn = document.getElementById('eraserBtn');
        const brushCursor = document.getElementById('brush-cursor');
        const toolSizeInput = document.getElementById('toolSize');
        let isDrawing = false;
        let active = false;
        let erasing = false;
        let currentColor = '#ff0000';

        const PALETTE = [
            ['#ff0000', '#ffffff', '#e8e8e8', '#cccccc', '#b3b3b3', '#999999', '#808080', '#666666', '#3f3f3f', '#1a1a1a'],
            ['#0a3a5a', '#0a1a5a', '#3a0a5a', '#5a0a3a', '#7a0a0a', '#7a2a0a', '#6a4a0a', '#5a5a0a', '#3a5a0a', '#0a4a0a'],
            ['#0a5a8a', '#0a2a8a', '#5a0a8a', '#8a0a5a', '#a01a1a', '#a03a0a', '#8a5a0a', '#7a7a0a', '#4a7a0a', '#0a6a0a'],
            ['#1a7aaa', '#1a3aaa', '#7a1aaa', '#aa1a7a', '#c02a2a', '#c04a0a', '#aa7a0a', '#9a9a0a', '#5a9a0a', '#1a8a1a'],
            ['#2a9aca', '#2a5aca', '#9a2aca', '#ca2a9a', '#e03a3a', '#e05a0a', '#ca9a0a', '#baba0a', '#6aba0a', '#2aaa2a'],
            ['#4abaea', '#4a7aea', '#ba4aea', '#ea4aba', '#f06a6a', '#f08a2a', '#eaba2a', '#dada2a', '#8ada2a', '#4aca4a'],
            ['#7adafa', '#7aaafa', '#da7afa', '#fa7ada', '#fa9a9a', '#faaa6a', '#fada6a', '#fafa6a', '#aafa6a', '#7aea7a'],
            ['#baeafa', '#bad6fa', '#eabafa', '#fabaea', '#facaca', '#fad6aa', '#faeaaa', '#fafaaa', '#dafaaa', '#bafaca']
        ];

        const palettePanel = document.getElementById('palette-panel');
        const colorPickerBtn = document.getElementById('colorPickerBtn');

        // Восстановить сохранённый размер кисти
        (function initToolSize() {
            const saved = localStorage.getItem('toolSize');
            if (saved) toolSizeInput.value = saved;
        })();

        // === Размер кисти / ластика ===
        function applyToolSize() {
            const d = parseInt(toolSizeInput.value, 10);
            brushCursor.style.width = d + 'px';
            brushCursor.style.height = d + 'px';
            ctx.lineWidth = d;
            localStorage.setItem('toolSize', d);
        }

        // === Установка инструментов ===
        function setBrush(color) {
            erasing = false;
            eraserBtn.classList.remove('active');
            eraserBtn.textContent = '🧽 Стереть';
            brushCursor.classList.remove('mode-eraser');
            brushCursor.classList.add('mode-brush');
            brushCursor.style.color = color;
            ctx.globalCompositeOperation = 'source-over';
            ctx.strokeStyle = color;
            currentColor = color;
            colorPickerBtn.style.background = color;
            applyToolSize();
        }

        function setEraser() {
            erasing = true;
            eraserBtn.classList.add('active');
            eraserBtn.textContent = '🧽 АКТИВЕН';
            brushCursor.classList.remove('mode-brush');
            brushCursor.classList.add('mode-eraser');
            ctx.globalCompositeOperation = 'destination-out';
            ctx.strokeStyle = 'rgba(0,0,0,1)';
            applyToolSize();
        }

        function toggleEraser() {
            if (erasing) {
                setBrush(currentColor);
            } else {
                setEraser();
            }
        }

        // === Палитра ===
        function buildPalette() {
            const palette = document.getElementById('palette');
            palette.innerHTML = '';
            PALETTE.forEach(row => {
                row.forEach(color => {
                    const d = document.createElement('div');
                    d.className = 'swatch';
                    d.style.background = color;
                    d.addEventListener('click', () => {
                        setBrush(color);
                        document.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
                        d.classList.add('active');
                    });
                    palette.appendChild(d);
                });
            });
        }

        if (colorPickerBtn) {
            colorPickerBtn.addEventListener('click', () => {
                palettePanel.classList.toggle('open');
            });
        }

        if (eraserBtn) {
            eraserBtn.addEventListener('click', toggleEraser);
        }

        if (toolSizeInput) {
            toolSizeInput.addEventListener('input', applyToolSize);
        }

        function clearCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        function clearCanvasConfirm() {
            const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            let hasInk = false;
            for (let i = 3; i < imgData.data.length; i += 4) {
                if (imgData.data[i] !== 0) { hasInk = true; break; }
            }
            if (hasInk && !confirm('Очистить все пометки?')) return;
            clearCanvas();
        }

        function saveCanvas() {
            let imgSrc = null;
            const fancyImg = document.querySelector('.fancybox__slide.is-selected img');
            if (fancyImg) {
                imgSrc = fancyImg.src;
            } else {
                const firstImg = document.querySelector('.gallery-item img');
                if (firstImg) imgSrc = firstImg.src;
            }

            const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);

            const doSave = (baseImg) => {
                const out = document.createElement('canvas');
                out.width = canvas.width;
                out.height = canvas.height;
                const octx = out.getContext('2d');
                if (baseImg) {
                    octx.drawImage(baseImg, 0, 0, out.width, out.height);
                }
                octx.drawImage(canvas, 0, 0);
                const link = document.createElement('a');
                link.download = `разбор_${ts}.png`;
                link.href = out.toDataURL('image/png');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            };

            if (imgSrc) {
                const img = new Image();
                img.crossOrigin = 'anonymous';
                img.onload = () => doSave(img);
                img.onerror = () => doSave(null);
                img.src = imgSrc;
            } else {
                doSave(null);
            }
        }

        function resizeCanvas() {
            if (!active) return;
            const snapshot = canvas.toDataURL();
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            ctx.lineCap = 'round';
            if (erasing) {
                ctx.globalCompositeOperation = 'destination-out';
                ctx.strokeStyle = 'rgba(0,0,0,1)';
            } else {
                ctx.globalCompositeOperation = 'source-over';
                ctx.strokeStyle = currentColor;
            }
            applyToolSize();
            const img = new Image();
            img.onload = () => ctx.drawImage(img, 0, 0);
            img.src = snapshot;
        }

        window.addEventListener('resize', resizeCanvas);

        function toggleReview() {
            active = !active;
            if (active) {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                ctx.lineCap = 'round';
                setBrush(currentColor);
                canvas.classList.add('active');
                tools.style.display = 'flex';
                toggleBtn.classList.add('active');
                toggleBtn.textContent = '✏️ Разбор (вкл)';
                document.body.classList.add('review-active');
            } else {
                canvas.classList.remove('active');
                tools.style.display = 'none';
                toggleBtn.classList.remove('active');
                toggleBtn.textContent = '✏️ Разбор';
                palettePanel.classList.remove('open');
                document.body.classList.remove('review-active');
                brushCursor.classList.remove('visible');
                eraserBtn.classList.remove('active');
                eraserBtn.textContent = '🧽 Стереть';
                erasing = false;
                ctx.globalCompositeOperation = 'source-over';
            }
        }

        toggleBtn.addEventListener('click', toggleReview);

        function startDraw(x, y) {
            isDrawing = true;
            ctx.beginPath();
            ctx.moveTo(x, y);
        }
        function moveDraw(x, y) {
            if (!isDrawing) return;
            ctx.lineTo(x, y);
            ctx.stroke();
        }

        canvas.addEventListener('mousedown', (e) => { if(!active) return; startDraw(e.clientX, e.clientY); });
        canvas.addEventListener('mousemove', (e) => {
            if (!active) return;
            brushCursor.style.left = e.clientX + 'px';
            brushCursor.style.top = e.clientY + 'px';
            brushCursor.classList.add('visible');
            if (isDrawing) moveDraw(e.clientX, e.clientY);
        });
        canvas.addEventListener('mouseup', () => isDrawing = false);
        canvas.addEventListener('mouseleave', () => {
            isDrawing = false;
            brushCursor.classList.remove('visible');
        });

        canvas.addEventListener('touchstart', (e) => {
            if (!active) return; e.preventDefault(); const t = e.touches[0];
            brushCursor.style.left = t.clientX + 'px';
            brushCursor.style.top = t.clientY + 'px';
            brushCursor.classList.add('visible');
            startDraw(t.clientX, t.clientY);
        });
        canvas.addEventListener('touchmove', (e) => {
            if (!active || !isDrawing) return; e.preventDefault(); const t = e.touches[0];
            brushCursor.style.left = t.clientX + 'px';
            brushCursor.style.top = t.clientY + 'px';
            moveDraw(t.clientX, t.clientY);
        });
        canvas.addEventListener('touchend', () => {
            isDrawing = false;
            brushCursor.classList.remove('visible');
        });

buildPalette(); // Этот
setBrush('#ff0000');  // и этот остался в конце файла - "монолита"


// Вставляю второй кусок из файла - "монолита"


        Fancybox.bind('[data-fancybox]', {
            Carousel: { infinite: false },
            on: {
                ready: () => document.body.classList.add('fancybox-open'),
                close: () => {
                    document.body.classList.remove('fancybox-open');
                    if (active) toggleReview();
                    clearCanvas();
                },
                destroy: () => document.body.classList.remove('fancybox-open'),
                'Carousel.change': () => clearCanvas()
            }
        });

        // Страховка: если оверлей Fancybox удалён из DOM, снимаем класс
        const fancyObserver = new MutationObserver(() => {
            if (!document.querySelector('.fancybox__container')) {
                document.body.classList.remove('fancybox-open');
            }
        });
        fancyObserver.observe(document.body, { childList: true, subtree: false });

