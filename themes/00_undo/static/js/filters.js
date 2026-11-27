document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('tagFilters');
    if (!root) return;

    const checkboxes = root.querySelectorAll('.filter-checkbox');
    const groups = root.querySelectorAll('.filter-group');
    const STORAGE_KEY = 'filterState_modern_v1';

    let saved = {};
    try {
        saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch (e) {}

    checkboxes.forEach(cb => {
        if (Object.prototype.hasOwnProperty.call(saved, cb.value)) {
            cb.checked = !!saved[cb.value];
        }
    });

    groups.forEach(group => {
        group.addEventListener('toggle', () => {
            if (group.open) {
                groups.forEach(other => {
                    if (other !== group && other.open) other.open = false;
                });
            }
        });

        const master = group.querySelector('.group-master-cb');
        const masterLabel = group.querySelector('.group-master');
        if (master) {
            const stop = (e) => e.stopPropagation();
            master.addEventListener('click', stop);
            if (masterLabel) masterLabel.addEventListener('click', stop);
            master.addEventListener('click', (e) => {
                e.preventDefault();
                const boxes = [...group.querySelectorAll('.filter-checkbox')];
                const allOn = boxes.length > 0 && boxes.every(b => b.checked);
                boxes.forEach(b => { b.checked = !allOn; });
                applyFilters();
            });
        }
    });

    document.addEventListener('click', (e) => {
        if (!root.contains(e.target)) {
            groups.forEach(g => { g.open = false; });
        }
    });

    function applyFilters() {
        const galleryItems = document.querySelectorAll('.gallery-item');
        const authorBlocks = document.querySelectorAll('.author-block');

        const activeTags = new Set();
        const activeNews = new Set();
        let anyTagFilterExists = false;

        checkboxes.forEach(cb => {
            if (cb.classList.contains('new-checkbox')) {
                if (cb.checked) activeNews.add(cb.value);
            } else {
                anyTagFilterExists = true;
                if (cb.checked) activeTags.add(cb.value);
            }
        });

        const hasActiveTagFilter = activeTags.size > 0;
        const hasNewCheckboxes = root.querySelectorAll('.new-checkbox').length > 0;

        galleryItems.forEach(item => {
            const tags = (item.dataset.tags || '').split(/\s+/).filter(Boolean);
            const newIdx = item.dataset.new;

            let tagOk = true;
            if (anyTagFilterExists) {
                if (!hasActiveTagFilter) {
                    tagOk = false;
                } else if (tags.length === 0) {
                    tagOk = true;
                } else {
                    tagOk = tags.some(t => activeTags.has(t));
                }
            }

            let newOk = true;
            if (newIdx !== undefined && newIdx !== '' && hasNewCheckboxes) {
                newOk = activeNews.has('new_' + newIdx);
            }

            item.style.display = (tagOk && newOk) ? '' : 'none';
        });

        authorBlocks.forEach(block => {
            const visible = [...block.querySelectorAll('.gallery-item')]
                .some(el => el.style.display !== 'none');
            block.style.display = visible ? '' : 'none';
        });

        const state = {};
        checkboxes.forEach(cb => { state[cb.value] = cb.checked; });
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));

        updateGroupCounts();
    }

    function updateGroupCounts() {
        groups.forEach(group => {
            const boxes = [...group.querySelectorAll('.filter-checkbox')];
            const checked = boxes.filter(b => b.checked).length;
            const badge = group.querySelector('.filter-count');
            if (badge) {
                badge.textContent = checked + '/' + boxes.length;
                badge.classList.toggle('partial', checked !== boxes.length);
                badge.classList.toggle('none', checked === 0);
            }
            const master = group.querySelector('.group-master-cb');
            const masterLabel = group.querySelector('.group-master');
            if (master) {
                master.checked = boxes.length > 0 && checked === boxes.length;
                master.indeterminate = checked > 0 && checked < boxes.length;
                if (masterLabel) {
                    masterLabel.title = master.indeterminate
                        ? 'Выбрано частично'
                        : (master.checked ? 'Выбрано всё' : 'Не выбрано ничего');
                }
            }
        });
    }

    checkboxes.forEach(cb => cb.addEventListener('change', applyFilters));
    applyFilters();
});
