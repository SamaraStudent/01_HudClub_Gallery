        const sizeSlider = document.getElementById('sizeSlider');
        const savedSize = localStorage.getItem('thumbSize') || '450';
        sizeSlider.value = savedSize;
        document.documentElement.style.setProperty('--thumb-size', savedSize + 'px');

        sizeSlider.addEventListener('input', function() {
            const val = this.value + 'px';
            document.documentElement.style.setProperty('--thumb-size', val);
            localStorage.setItem('thumbSize', this.value);
        });