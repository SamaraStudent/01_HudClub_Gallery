document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('.filter-checkbox');
    const resetBtn = document.getElementById('resetFiltersBtn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    const authorBlocks = document.querySelectorAll('.author-block');

    // Загрузка сохраненного состояния из памяти браузера
    const savedState = JSON.parse(localStorage.getItem('filterState_v2') || '{}');

    // Применяем сохраненное состояние к чекбоксам при загрузке
    checkboxes.forEach(cb => {
        if (savedState.hasOwnProperty(cb.value)) {
            cb.checked = savedState[cb.value];
        }
    });

    function applyFilters() {
        galleryItems.forEach(item => {
            const tags = (item.dataset.tags || '').split(/\s+/).filter(Boolean);
            const itemNewIdx = item.dataset.new; // ID "нового" задания

            // 1. Проверяем совпадение по хештегам (элемент виден, если выбран хотя бы один тег)
            let tagMatch = tags.some(tag => {
                const cb = document.querySelector(`.filter-checkbox[value="${tag}"]`);
                return cb ? cb.checked : true;
            });

            // 2. Проверяем фильтр "Новые"
            let newMatch = true;
            if (itemNewIdx !== undefined && itemNewIdx !== "") {
                const newCb = document.querySelector(`.filter-checkbox[value="new_${itemNewIdx}"]`);
                if (newCb && !newCb.checked) {
                    newMatch = false;
                }
            }

            // Итоговое решение
            const isVisible = tagMatch && newMatch;
            item.style.display = isVisible ? '' : 'none';
        });

        // Скрываем блоки авторов, у которых не осталось видимых картинок
        authorBlocks.forEach(block => {
            const hasVisible = [...block.querySelectorAll('.gallery-item')].some(c => c.style.display !== 'none');
            block.style.display = hasVisible ? '' : 'none';
        });

        // Сохраняем новое состояние
        const newState = {};
        checkboxes.forEach(cb => { newState[cb.value] = cb.state || cb.checked; });
        localStorage.setItem('filterState_v2', JSON.stringify(newState));
    }

    checkboxes.forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            checkboxes.forEach(cb => { cb.checked = true; });
            applyFilters();
        });
    }

    applyFilters();
});
