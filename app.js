let allLessons = [];
let filteredLessons = [];

async function loadLessons() {
    try {
        const response = await fetch('lessons.json');
        allLessons = await response.json();
        filteredLessons = [...allLessons];
        
        populateFilters();
        renderLessons();
    } catch (error) {
        document.getElementById('lessons-grid').innerHTML = 
            '<div class="loading">Error loading lessons. Please try again later.</div>';
        console.error('Error loading lessons:', error);
    }
}

function populateFilters() {
    const topics = new Set();
    const models = new Set();
    
    allLessons.forEach(lesson => {
        if (lesson.topic && lesson.topic !== 'NA') {
            topics.add(lesson.topic);
        }
        if (lesson.model) {
            models.add(lesson.model);
        }
    });
    
    const topicSelect = document.getElementById('filter-topic');
    const modelSelect = document.getElementById('filter-model');
    
    Array.from(topics).sort().forEach(topic => {
        const option = document.createElement('option');
        option.value = topic;
        option.textContent = topic;
        topicSelect.appendChild(option);
    });
    
    Array.from(models).sort().forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
}

function applyFilters() {
    const typeFilter = document.getElementById('filter-type').value;
    const topicFilter = document.getElementById('filter-topic').value;
    const modelFilter = document.getElementById('filter-model').value;
    const dateFilter = document.getElementById('filter-date').value;
    
    filteredLessons = allLessons.filter(lesson => {
        if (typeFilter && lesson.type !== typeFilter) return false;
        if (topicFilter && lesson.topic !== topicFilter) return false;
        if (modelFilter && lesson.model !== modelFilter) return false;
        if (dateFilter && lesson.date !== dateFilter) return false;
        return true;
    });
    
    renderLessons();
}

function resetFilters() {
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-topic').value = '';
    document.getElementById('filter-model').value = '';
    document.getElementById('filter-date').value = '';
    
    filteredLessons = [...allLessons];
    renderLessons();
}

function renderLessons() {
    const grid = document.getElementById('lessons-grid');
    
    if (filteredLessons.length === 0) {
        grid.innerHTML = '<div class="loading">No lessons found matching your filters.</div>';
        return;
    }
    
    grid.innerHTML = filteredLessons.map(lesson => createCard(lesson)).join('');
    
    document.querySelectorAll('.lesson-card').forEach((card, index) => {
        card.addEventListener('click', () => openModal(filteredLessons[index]));
    });
}

function createCard(lesson) {
    const content = lesson.content || 'No content available';
    const preview = stripMarkdown(content).substring(0, 150) + '...';
    const badgeClass = lesson.type === 'news' ? 'badge-news' : 'badge-topic';
    const displayTopic = lesson.topic === 'NA' ? 'Daily News' : lesson.topic;
    
    return `
        <div class="lesson-card">
            <div class="card-header">
                <div class="card-date">${formatDate(lesson.date)}</div>
                <div class="card-badges">
                    <span class="badge ${badgeClass}">${lesson.type}</span>
                </div>
            </div>
            <h3 class="card-topic">${displayTopic}</h3>
            <p class="card-preview">${preview}</p>
            <div class="card-footer">
                <span class="card-model">${lesson.model}</span>
                <span class="read-more">Read more →</span>
            </div>
        </div>
    `;
}

function stripMarkdown(text) {
    return text
        .replace(/#{1,6}\s?/g, '')
        .replace(/\*\*(.+?)\*\*/g, '$1')
        .replace(/\*(.+?)\*/g, '$1')
        .replace(/\[(.+?)\]\(.+?\)/g, '$1')
        .replace(/`(.+?)`/g, '$1')
        .replace(/>\s?/g, '')
        .replace(/\n+/g, ' ')
        .trim();
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

function openModal(lesson) {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    
    const displayTopic = lesson.topic === 'NA' ? 'Daily News Summary' : lesson.topic;
    const badgeClass = lesson.type === 'news' ? 'badge-news' : 'badge-topic';
    
    const content = lesson.content || 'Content not available due to API limits.';
    const vocabulary = lesson.vocabulary || 'Vocabulary not available.';
    const contentHtml = marked.parse(content);
    const vocabularyHtml = marked.parse(vocabulary);
    
    modalBody.innerHTML = `
        <div class="modal-header">
            <h2 class="modal-title">${displayTopic}</h2>
            <div class="modal-meta">
                <div class="modal-meta-item">
                    <span class="badge ${badgeClass}">${lesson.type}</span>
                </div>
                <div class="modal-meta-item">
                    📅 ${formatDate(lesson.date)}
                </div>
                <div class="modal-meta-item">
                    🤖 ${lesson.model}
                </div>
            </div>
        </div>
        
        <div class="modal-section">
            <h3 class="section-title">${lesson.type === 'news' ? 'News Summary' : 'Discussion'}</h3>
            <div class="markdown-content">
                ${contentHtml}
            </div>
        </div>
        
        <div class="modal-section">
            <h3 class="section-title">📚 Vocabulary</h3>
            <div class="markdown-content">
                ${vocabularyHtml}
            </div>
        </div>
    `;
    
    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('active');
}

document.addEventListener('DOMContentLoaded', () => {
    loadLessons();
    
    document.getElementById('filter-type').addEventListener('change', applyFilters);
    document.getElementById('filter-topic').addEventListener('change', applyFilters);
    document.getElementById('filter-model').addEventListener('change', applyFilters);
    document.getElementById('filter-date').addEventListener('change', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
    
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.addEventListener('click', closeModal);
    
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
    
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
});
