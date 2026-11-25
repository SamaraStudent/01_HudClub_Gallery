        // === Фильтры ===
        const tagFilters = document.querySelector('.tag-filters');
        if (tagFilters) {
            const filterBtns = document.querySelectorAll('.filter-btn');
            const KEY = 'filterState';

            let state;
            try {
                state = JSON.parse(localStorage.getItem(KEY) || '{}');
            } catch (e) {
                state = {};
            }

            function getState(key, defVal) {
                return (key in state) ? state[key] : defVal;
            }

            function syncButtons() {
                filterBtns.forEach(btn => {
                    const isOff = !getState(btn.dataset.filter, btn.dataset.filterType === 'tag');
                    btn.classList.toggle('off', isOff);
                });
            }

            function applyFilters() {
                document.querySelectorAll('.gallery-item').forEach(item => {
                    const tags = (item.dataset.tags || '').split(/\\s+/).filter(Boolean);
                    const hiddenByTag = tags.some(t => !getState(t, true));

                    let hiddenByNew = false;
                    if (item.dataset.new) {
                        const idx = item.dataset.new;
                        const key = 'new_' + idx;
                        const anyNewActive = [...document.querySelectorAll('.filter-btn[data-filter-type="new"]')]
                            .some(b => getState(b.dataset.filter, false));
                        if (anyNewActive) {
                            hiddenByNew = !getState(key, false);
                        }
                    }

                    item.style.display = (hiddenByTag || hiddenByNew) ? 'none' : '';
                });
                document.querySelectorAll('.author-block').forEach(block => {
                    const visible = [...block.querySelectorAll('.gallery-item')]
                        .some(c => c.style.display !== 'none');
                    block.style.display = visible ? '' : 'none';
                });
            }

            filterBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const key = btn.dataset.filter;
                    const defVal = btn.dataset.filterType === 'tag';
                    state[key] = !getState(key, defVal);
                    localStorage.setItem(KEY, JSON.stringify(state));
                    syncButtons();
                    applyFilters();
                });
            });

            syncButtons();
            applyFilters();
        }