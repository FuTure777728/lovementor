/**
 * 情感良师 LoveMentor — 前端交互逻辑
 */

// ============================================================
// 全局状态
// ============================================================

const state = {
    currentTab: 'chat',
    isAnalyzing: false,
    zodiacSigns: [],
    currentUser: localStorage.getItem('lovementor_user') || '水水',
};

// ============================================================
// DOM 元素
// ============================================================

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// 导航
const navTabs = $('#navTabs');
const tabContents = $$('.tab-content');

// 聊天
const chatWelcome = $('#chatWelcome');
const chatMessages = $('#chatMessages');
const chatInput = $('#chatInput');
const sendBtn = $('#sendBtn');
const sentimentBar = $('#sentimentBar');
const sentimentTag = $('#sentimentTag');
const sentimentEmotions = $('#sentimentEmotions');
const charCount = $('#charCount');
const hintChips = $$('.hint-chip');

// 星座
const matchSign1 = $('#matchSign1');
const matchSign2 = $('#matchSign2');
const matchBtn = $('#matchBtn');
const matchResult = $('#matchResult');
const fortuneSign = $('#fortuneSign');
const fortuneBtn = $('#fortuneBtn');
const fortuneResult = $('#fortuneResult');

// 历史
const historyList = $('#historyList');
const clearHistoryBtn = $('#clearHistoryBtn');

// Loading
const loadingOverlay = $('#loadingOverlay');

// ============================================================
// 通用工具
// ============================================================

function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function formatTime(isoString) {
    const d = new Date(isoString);
    const now = new Date();
    const diff = now - d;
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
    return d.toLocaleString('zh-CN', {
        month: 'numeric', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// Tab 切换
// ============================================================

navTabs.addEventListener('click', (e) => {
    const tabBtn = e.target.closest('.nav-tab');
    if (!tabBtn) return;

    const tabName = tabBtn.dataset.tab;
    if (tabName === state.currentTab) return;

    // 切换导航激活状态
    $$('.nav-tab').forEach(t => t.classList.remove('active'));
    tabBtn.classList.add('active');

    // 切换内容区
    tabContents.forEach(tc => tc.classList.remove('active'));
    $(`#tab-${tabName}`).classList.add('active');

    state.currentTab = tabName;

    // 切换到对应 Tab 时刷新数据
    if (tabName === 'history') {
        loadHistory();
    } else if (tabName === 'mailbox') {
        loadInbox();
        updateUnreadBadge();
    } else if (tabName === 'mediation') {
        loadMediationState();
    }
});

// ============================================================
// Tab 1: 情感倾诉
// ============================================================

// 提示词点击
hintChips.forEach(chip => {
    chip.addEventListener('click', () => {
        chatInput.value = chip.dataset.text;
        chatInput.focus();
        updateCharCount();
    });
});

// 发送按钮
sendBtn.addEventListener('click', () => sendMessage());

// 键盘事件
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// 字数统计
chatInput.addEventListener('input', updateCharCount);

function updateCharCount() {
    const len = chatInput.value.length;
    charCount.textContent = len;
    charCount.style.color = len > 1800 ? '#d49592' : '';
}

function sendMessage() {
    const text = chatInput.value.trim();
    if (!text || state.isAnalyzing) return;

    state.isAnalyzing = true;
    sendBtn.disabled = true;

    // 隐藏欢迎区
    chatWelcome.classList.add('hidden');

    // 显示用户消息
    appendMessage('user', text);
    chatInput.value = '';
    updateCharCount();

    // 添加加载中的 AI 消息占位
    const loadingMsg = appendMessage('ai', '<span class="typing-indicator">白开水正在冒泡<span class="dots">...</span></span>', true);
    const loadingEl = loadingMsg;

    showLoading();

    // 调用 API
    fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, user: state.currentUser }),
    })
    .then(res => res.json())
    .then(data => {
        hideLoading();

        // 移除加载占位
        if (loadingEl) loadingEl.remove();

        if (data.error) {
            appendMessage('ai', `😔 ${data.error}`);
            hideSentimentBar();
            return;
        }

        // 显示情感标签
        showSentimentBar(data.sentiment);

        // 显示 AI 回应
        appendMessage('ai', data.response);
    })
    .catch(err => {
        hideLoading();
        if (loadingEl) loadingEl.remove();
        appendMessage('ai', '😔 抱歉，网络连接出现了问题，请稍后再试...');
        hideSentimentBar();
    })
    .finally(() => {
        state.isAnalyzing = false;
        sendBtn.disabled = false;
        chatInput.focus();
    });
}

function appendMessage(role, content, isPlaceholder = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    if (isPlaceholder) msgDiv.classList.add('message-placeholder');

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '💝' : '🐼';

    const bubbleWrap = document.createElement('div');
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = content;

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = formatTime(new Date().toISOString());

    bubbleWrap.appendChild(bubble);
    bubbleWrap.appendChild(time);

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubbleWrap);

    chatMessages.appendChild(msgDiv);

    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return msgDiv;
}

function showSentimentBar(sentiment) {
    if (!sentiment) {
        hideSentimentBar();
        return;
    }

    const { label, category, emotions } = sentiment;

    sentimentTag.textContent = `💡 ${label || '分析中...'}`;
    sentimentTag.className = `sentiment-tag ${category || 'neutral'}`;

    sentimentEmotions.innerHTML = '';
    if (emotions && emotions.length) {
        emotions.forEach(em => {
            const dot = document.createElement('span');
            dot.className = 'emotion-dot';
            dot.textContent = em;
            sentimentEmotions.appendChild(dot);
        });
    }

    sentimentBar.style.display = 'flex';
}

function hideSentimentBar() {
    sentimentBar.style.display = 'none';
}

// ============================================================
// Tab 2: 星座分析
// ============================================================

// 加载星座列表
function loadZodiacSigns() {
    fetch('/api/zodiac/list')
        .then(res => res.json())
        .then(data => {
            state.zodiacSigns = data.signs || [];
            populateSignSelects();
        })
        .catch(() => {
            // 硬编码降级
            state.zodiacSigns = [
                {name:"白羊座",emoji:"♈"},{name:"金牛座",emoji:"♉"},{name:"双子座",emoji:"♊"},
                {name:"巨蟹座",emoji:"♋"},{name:"狮子座",emoji:"♌"},{name:"处女座",emoji:"♍"},
                {name:"天秤座",emoji:"♎"},{name:"天蝎座",emoji:"♏"},{name:"射手座",emoji:"♐"},
                {name:"摩羯座",emoji:"♑"},{name:"水瓶座",emoji:"♒"},{name:"双鱼座",emoji:"♓"},
            ];
            populateSignSelects();
        });
}

function populateSignSelects() {
    const options = state.zodiacSigns.map(s =>
        `<option value="${s.name}">${s.emoji} ${s.name}</option>`
    ).join('');

    [matchSign1, matchSign2, fortuneSign].forEach(select => {
        const placeholder = select.querySelector('option[value=""]');
        select.innerHTML = (placeholder ? placeholder.outerHTML : '<option value="">选择星座</option>') + options;
    });
}

// 星座匹配
matchBtn.addEventListener('click', () => {
    const sign1 = matchSign1.value;
    const sign2 = matchSign2.value;

    if (!sign1 || !sign2) {
        matchResult.style.display = 'block';
        matchResult.innerHTML = '<p style="color:#d49592;text-align:center;">请选择两个星座</p>';
        return;
    }

    if (sign1 === sign2) {
        matchResult.style.display = 'block';
        matchResult.innerHTML = '<p style="color:#c9a96e;text-align:center;">同一个星座也可以很配哦～让我来分析分析 ✨</p>';
    }

    matchBtn.disabled = true;
    matchBtn.innerHTML = '<span>⏳</span> 分析中...';
    showLoading();

    fetch('/api/zodiac/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sign1, sign2 }),
    })
    .then(res => res.json())
    .then(data => {
        hideLoading();
        if (data.error) {
            matchResult.style.display = 'block';
            matchResult.innerHTML = `<p style="color:#d49592;text-align:center;">${escapeHtml(data.error)}</p>`;
            return;
        }
        renderMatchResult(data);
    })
    .catch(() => {
        hideLoading();
        matchResult.style.display = 'block';
        matchResult.innerHTML = '<p style="color:#d49592;text-align:center;">网络请求失败，请稍后重试</p>';
    })
    .finally(() => {
        matchBtn.disabled = false;
        matchBtn.innerHTML = '<span>✨</span> 查看匹配度';
    });
});

function renderMatchResult(data) {
    const sign1Info = state.zodiacSigns.find(s => s.name === data.sign1);
    const sign2Info = state.zodiacSigns.find(s => s.name === data.sign2);

    const html = `
        <div class="match-score-circle">
            <span class="match-score-number">${data.compatibility_score}</span>
            <span class="match-score-label">匹配指数</span>
        </div>
        <div class="match-level">${data.level || ''}</div>
        <div class="match-level-desc">${data.level_desc || ''}</div>
        <div class="match-analysis">${escapeHtml(data.analysis || '')}</div>
        ${(data.strengths && data.strengths.length) ? `
        <div class="match-detail-section">
            <h4>💕 优势</h4>
            <ul>${data.strengths.map(s => `<li>${escapeHtml(s)}</li>`).join('')}</ul>
        </div>` : ''}
        ${(data.challenges && data.challenges.length) ? `
        <div class="match-detail-section">
            <h4>🤔 需要注意</h4>
            <ul>${data.challenges.map(c => `<li>${escapeHtml(c)}</li>`).join('')}</ul>
        </div>` : ''}
        ${data.advice ? `
        <div class="match-detail-section">
            <h4>💌 白开水的建议</h4>
            <p style="font-size:14px;color:var(--brown-light);line-height:1.7;">${escapeHtml(data.advice)}</p>
        </div>` : ''}
        ${data.romance_tip ? `
        <div style="margin-top:10px;padding:10px 14px;background:rgba(201,169,110,0.08);border-radius:10px;font-size:13px;color:var(--brown-light);">
            🌹 ${escapeHtml(data.romance_tip)}
        </div>` : ''}
    `;

    matchResult.innerHTML = html;
    matchResult.style.display = 'block';
    matchResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 今日运势
fortuneBtn.addEventListener('click', () => {
    const sign = fortuneSign.value;
    if (!sign) {
        fortuneResult.style.display = 'block';
        fortuneResult.innerHTML = '<p style="color:#d49592;text-align:center;">请选择一个星座</p>';
        return;
    }

    fortuneBtn.disabled = true;
    fortuneBtn.innerHTML = '<span>⏳</span> 占星中...';
    showLoading();

    fetch('/api/zodiac/fortune', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sign }),
    })
    .then(res => res.json())
    .then(data => {
        hideLoading();
        if (data.error) {
            fortuneResult.style.display = 'block';
            fortuneResult.innerHTML = `<p style="color:#d49592;text-align:center;">${escapeHtml(data.error)}</p>`;
            return;
        }
        renderFortuneResult(data);
    })
    .catch(() => {
        hideLoading();
        fortuneResult.style.display = 'block';
        fortuneResult.innerHTML = '<p style="color:#d49592;text-align:center;">网络请求失败，请稍后重试</p>';
    })
    .finally(() => {
        fortuneBtn.disabled = false;
        fortuneBtn.innerHTML = '<span>🔮</span> 查看今日运势';
    });
});

function renderFortuneResult(data) {
    const html = `
        <div class="fortune-summary">${escapeHtml(data.fortune_summary || '')}</div>
        <div class="fortune-details">
            <div class="fortune-item">
                <div class="fi-label">爱情指数</div>
                <div class="fi-value">${data.love_index || '⭐⭐⭐'}</div>
            </div>
            <div class="fortune-item">
                <div class="fi-label">幸运色</div>
                <div class="fi-value">${escapeHtml(data.lucky_color || '—')}</div>
            </div>
            <div class="fortune-item">
                <div class="fi-label">幸运数字</div>
                <div class="fi-value">${data.lucky_number || '—'}</div>
            </div>
            <div class="fortune-item">
                <div class="fi-label">元素</div>
                <div class="fi-value">${escapeHtml(data.element || '—')}</div>
            </div>
        </div>
        ${data.today_tip ? `
        <div class="fortune-tip">
            <strong>💫 今日小贴士：</strong>${escapeHtml(data.today_tip)}
        </div>` : ''}
        ${data.mood_advice ? `
        <div class="fortune-tip" style="margin-top:8px;">
            <strong>💝 暖心建议：</strong>${escapeHtml(data.mood_advice)}
        </div>` : ''}
    `;

    fortuneResult.innerHTML = html;
    fortuneResult.style.display = 'block';
    fortuneResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================================
// Tab 3: 心情记录
// ============================================================

function loadHistory() {
    historyList.innerHTML = '<div class="history-empty"><span class="empty-icon">⏳</span><p>加载中...</p></div>';

    fetch('/api/history?limit=50')
        .then(res => res.json())
        .then(data => {
            if (!data.records || data.records.length === 0) {
                historyList.innerHTML = `
                    <div class="history-empty">
                        <span class="empty-icon">📝</span>
                        <p>还没有记录，去倾诉一下心情吧</p>
                    </div>`;
                return;
            }
            renderHistory(data.records);
        })
        .catch(() => {
            historyList.innerHTML = `
                <div class="history-empty">
                    <span class="empty-icon">😔</span>
                    <p>加载失败，请稍后重试</p>
                </div>`;
        });
}

function renderHistory(records) {
    historyList.innerHTML = records.map(r => {
        const time = formatTime(r.created_at);
        const tagClass = r.sentiment_category || 'neutral';
        return `
            <div class="history-item">
                <div class="history-item-time">${time}</div>
                <div class="history-item-user">"${escapeHtml(r.user_text)}"</div>
                <div class="history-item-response">${escapeHtml(r.ai_response)}</div>
                <span class="history-item-tag ${tagClass}">${escapeHtml(r.sentiment_label || '思考')}</span>
            </div>
        `;
    }).join('');
}

// 清空历史
clearHistoryBtn.addEventListener('click', () => {
    if (!confirm('确定要清空所有心情记录吗？这个操作不可撤销。')) return;

    fetch('/api/history', { method: 'DELETE' })
        .then(res => res.json())
        .then(() => {
            historyList.innerHTML = `
                <div class="history-empty">
                    <span class="empty-icon">📝</span>
                    <p>记录已清空。新的故事，从今天开始 💕</p>
                </div>`;
        })
        .catch(() => alert('清空失败，请稍后重试'));
});

// ============================================================
// 用户身份管理 (A1 + A2)
// ============================================================

const userSwitcher = $('#userSwitcher');
const userBtns = $$('.user-btn');
const welcomeAvatar = $('#welcomeAvatar');
const welcomeTitle = $('#welcomeTitle');
const welcomeDesc = $('#welcomeDesc');
const chatPlaceholder = $('#chatInputPlaceholder');

function switchUser(userName) {
    if (state.currentUser === userName) return;
    state.currentUser = userName;
    localStorage.setItem('lovementor_user', userName);
    applyUserUI();
}

function applyUserUI() {
    const u = state.currentUser;
    // 按钮状态
    userBtns.forEach(b => b.classList.toggle('active', b.dataset.user === u));
    // 欢迎语
    if (u === '水水') {
        welcomeAvatar.textContent = '🐼';
        welcomeTitle.textContent = '嗨水水，我是白开水～';
        welcomeDesc.innerHTML = '兄dei，不管是甜蜜还是烦恼，<br>哥们都在这儿帮你参谋参谋！';
        chatPlaceholder.placeholder = '水水，说说你的心事吧...';
    } else {
        welcomeAvatar.textContent = '🐰';
        welcomeTitle.textContent = '嗨小白，我是白开水～';
        welcomeDesc.innerHTML = '姐妹来啦！无论是八卦还是心事，<br>我都搬好小板凳准备听了～';
        chatPlaceholder.placeholder = '小白，今天想聊什么呀～';
    }
    // 如果信箱 Tab 打开，刷新
    if (state.currentTab === 'mailbox') loadInbox();
    if (state.currentTab === 'mediation') loadMediationState();
}

userBtns.forEach(btn => {
    btn.addEventListener('click', () => switchUser(btn.dataset.user));
});

// 初次加载时应用
applyUserUI();

// ============================================================
// Tab 3: 情侣信箱 (B1)
// ============================================================

const letterMessage = $('#letterMessage');
const letterCharCount = $('#letterCharCount');
const sendLetterBtn = $('#sendLetterBtn');
const inboxList = $('#inboxList');
const inboxTitle = $('#inboxTitle');
const mailboxBadge = $('#mailboxBadge');

// 字母计数
letterMessage.addEventListener('input', () => {
    letterCharCount.textContent = letterMessage.value.length;
});

// 发送信件
sendLetterBtn.addEventListener('click', () => {
    const msg = letterMessage.value.trim();
    if (!msg) return;

    sendLetterBtn.disabled = true;
    sendLetterBtn.innerHTML = '<span>⏳</span> 飞鸽中...';

    fetch('/api/mailbox/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_user: state.currentUser, message: msg }),
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert(data.error); return; }
        letterMessage.value = '';
        letterCharCount.textContent = '0';
        const other = data.to_user;
        alert(`💌 已送达！${other}下次登录就能看到啦～`);
        loadInbox();
    })
    .catch(() => alert('发送失败，请稍后重试'))
    .finally(() => {
        sendLetterBtn.disabled = false;
        sendLetterBtn.innerHTML = '<span>💌</span> 飞鸽传书';
    });
});

function loadInbox() {
    inboxTitle.textContent = `${state.currentUser === '水水' ? '小白' : '水水'}写给你的信`;
    const other = state.currentUser === '水水' ? '小白' : '水水';

    fetch(`/api/mailbox/inbox?user=${state.currentUser}`)
        .then(res => res.json())
        .then(data => {
            if (!data.letters || data.letters.length === 0) {
                inboxList.innerHTML = `
                    <div class="history-empty">
                        <span class="empty-icon">📮</span>
                        <p>还没有收到信，期待${other}的第一封信吧～</p>
                    </div>`;
            } else {
                window._lettersCache = {};
                inboxList.innerHTML = data.letters.map(l => {
                    window._lettersCache[l.id] = l;
                    return `
                    <div class="letter-card ${l.is_read ? '' : 'unread'}" data-id="${l.id}">
                        <div class="letter-from">💌 来自 ${escapeHtml(l.from_user)}</div>
                        <div class="letter-preview">${escapeHtml(l.message.substring(0, 80))}${l.message.length > 80 ? '...' : ''}</div>
                        <div class="letter-time">${formatTime(l.created_at)}</div>
                        ${l.is_read ? '' : '<div class="unread-dot"></div>'}
                    </div>
                `}).join('');
            }
        })
        .catch(() => {
            inboxList.innerHTML = '<div class="history-empty"><p>加载失败</p></div>';
        });
}

// 信件卡片点击 — 使用事件委托
inboxList.addEventListener('click', (e) => {
    const card = e.target.closest('.letter-card');
    if (!card) return;
    const id = parseInt(card.dataset.id);
    const letter = window._lettersCache && window._lettersCache[id];
    if (!letter) return;

    const overlay = document.createElement('div');
    overlay.className = 'letter-modal-overlay';
    overlay.innerHTML = `
        <div class="letter-modal">
            <button class="modal-close">✕</button>
            <div class="modal-from">💌 ${escapeHtml(letter.from_user)} 写给你的信</div>
            <div class="modal-message">${escapeHtml(letter.message).replace(/\n/g, '<br>')}</div>
            <div class="modal-time">${formatTime(letter.created_at)}</div>
        </div>
    `;
    overlay.querySelector('.modal-close').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (ev) => {
        if (ev.target === overlay) overlay.remove();
    });
    document.body.appendChild(overlay);

    if (!letter.is_read) {
        fetch(`/api/mailbox/read/${id}`, { method: 'PUT' })
            .then(() => {
                letter.is_read = 1;
                updateUnreadBadge();
            });
    }
});

function updateUnreadBadge() {
    if (!state.currentUser) return;
    fetch(`/api/mailbox/unread?user=${state.currentUser}`)
        .then(res => res.json())
        .then(data => {
            if (data.count > 0) {
                mailboxBadge.textContent = data.count;
                mailboxBadge.style.display = 'inline-flex';
            } else {
                mailboxBadge.style.display = 'none';
            }
        })
        .catch(() => {});
}

// ============================================================
// Tab 4: 矛盾调解室 (B5)
// ============================================================

const mediationMessage = $('#mediationMessage');
const submitMediationBtn = $('#submitMediationBtn');
const mediationResult = $('#mediationResult');
const mediationInputArea = $('#mediationInputArea');
const mediationSteps = $('#mediationSteps');
const mediationPrompt = $('#mediationPrompt');
const mediationHistoryList = $('#mediationHistoryList');
const currentSessionKey = $('#currentSessionKey');

submitMediationBtn.addEventListener('click', () => {
    const msg = mediationMessage.value.trim();
    if (!msg) return;

    submitMediationBtn.disabled = true;
    submitMediationBtn.innerHTML = '<span>⏳</span> 提交中...';

    fetch('/api/mediation/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: state.currentUser, message: msg }),
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert(data.error); return; }
        mediationMessage.value = '';
        currentSessionKey.value = data.session_key;

        if (data.both_ready) {
            // 双方都提交了，自动触发分析
            loadMediationResult(data.session_key);
        } else {
            mediationPrompt.innerHTML = `<span class="prompt-icon">⏳</span><p>已记录你的视角！等 <strong>${data.waiting_for}</strong> 也来提交后，白开水就能帮你们分析啦～</p>`;
            updateMediationSteps(1);
        }
        loadMediationHistory();
    })
    .catch(() => alert('提交失败，请稍后重试'))
    .finally(() => {
        submitMediationBtn.disabled = false;
        submitMediationBtn.innerHTML = '<span>🤝</span> 提交我的视角';
    });
});

function loadMediationState() {
    // 检查是否有待处理的调解 session
    fetch('/api/mediation/history?limit=1')
        .then(res => res.json())
        .then(data => {
            if (data.records && data.records.length > 0) {
                const latest = data.records[0];
                if (latest.has_result) {
                    currentSessionKey.value = latest.session_key;
                    loadMediationResult(latest.session_key);
                } else if (latest.cnt < 2) {
                    currentSessionKey.value = latest.session_key;
                    fetch(`/api/mediation/status?session=${latest.session_key}`)
                        .then(r => r.json())
                        .then(s => {
                            if (!s.both_ready) {
                                mediationPrompt.innerHTML = `<span class="prompt-icon">⏳</span><p>已记录你的视角！等 <strong>${state.currentUser === '水水' ? '小白' : '水水'}</strong> 也来提交后，白开水就能帮你们分析啦～</p>`;
                                updateMediationSteps(1);
                            }
                        });
                }
            }
        })
        .finally(() => loadMediationHistory());
}

function loadMediationResult(sessionKey) {
    showLoading();
    fetch(`/api/mediation/result?session=${sessionKey}`)
        .then(res => res.json())
        .then(data => {
            hideLoading();
            if (!data.ready) {
                mediationResult.style.display = 'none';
                mediationInputArea.style.display = 'block';
                return;
            }
            renderMediationResult(data);
        })
        .catch(() => {
            hideLoading();
            mediationResult.innerHTML = '<p style="color:#d49592;">加载失败</p>';
            mediationResult.style.display = 'block';
        });
}

function renderMediationResult(data) {
    updateMediationSteps(3);
    mediationInputArea.style.display = 'none';
    mediationResult.style.display = 'block';

    mediationResult.innerHTML = `
        <div class="ice-breaker">${escapeHtml(data.ice_breaker || '来，白开水帮你们捋捋～ 🫧')}</div>
        <div class="perspectives">
            <div class="perspective-card">
                <h4>🐼 水水的视角</h4>
                <p>${escapeHtml(data.shuishui_view || '')}</p>
            </div>
            <div class="perspective-card">
                <h4>🐰 小白的视角</h4>
                <p>${escapeHtml(data.xiaobai_view || '')}</p>
            </div>
        </div>
        <div class="core-issue">
            <h4>💡 矛盾核心</h4>
            <p>${escapeHtml(data.core_issue || '')}</p>
        </div>
        <div class="advice-section">
            <strong>🤝 和解建议</strong><br>${escapeHtml(data.advice || '')}
        </div>
        <div class="sweet-action">${escapeHtml(data.sweet_action || '一起去吃顿好的吧！🍜')}</div>
    `;
    mediationResult.scrollIntoView({ behavior: 'smooth' });
}

function updateMediationSteps(currentStep) {
    const stepItems = $$('.step-item');
    const stepLines = $$('.step-line');
    stepItems.forEach((item, i) => {
        item.classList.remove('active', 'done');
        const step = parseInt(item.dataset.step);
        if (step < currentStep) item.classList.add('done');
        if (step === currentStep) item.classList.add('active');
    });
    stepLines.forEach((line, i) => {
        if (i < currentStep - 1) line.classList.add('done');
        else line.classList.remove('done');
    });
}

function loadMediationHistory() {
    fetch('/api/mediation/history?limit=10')
        .then(res => res.json())
        .then(data => {
            if (!data.records || data.records.length === 0) {
                mediationHistoryList.innerHTML = '<p class="empty-hint">还没有调解记录</p>';
                return;
            }
            mediationHistoryList.innerHTML = data.records.map(r => `
                <div class="mediation-history-item" onclick="loadMediationResult('${r.session_key}')">
                    <span>🕊️ ${r.users || '未知'}</span>
                    <span style="font-size:12px;color:var(--brown-lighter);">${formatTime(r.latest_time)}</span>
                    <span>${r.has_result ? '✅ 已分析' : '⏳ 等待中'}</span>
                </div>
            `).join('');
        })
        .catch(() => {
            mediationHistoryList.innerHTML = '<p class="empty-hint">加载失败</p>';
        });
}

// ============================================================
// 初始化
// ============================================================

function init() {
    loadZodiacSigns();
    updateCharCount();
    chatInput.focus();
    updateUnreadBadge();
    // 定时刷新未读数量
    setInterval(updateUnreadBadge, 30000);
}

init();
