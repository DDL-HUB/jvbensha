// ========== 状态管理 ==========
let currentScene = 'scene1';
let isTransitioning = false;

// ========== 音效播放 ==========
function playSound(soundId) {
    const sound = document.getElementById(soundId);
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(e => console.log('音频播放失败:', e));
    }
}

// ========== 波纹效果 ==========
function createRipple(event, button) {
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    
    ripple.style.width = ripple.style.height = size + 'px';
    
    if (event) {
        ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
        ripple.style.top = (event.clientY - rect.top - size / 2) + 'px';
    } else {
        // 键盘触发时，从中心开始
        ripple.style.left = (rect.width / 2 - size / 2) + 'px';
        ripple.style.top = (rect.height / 2 - size / 2) + 'px';
    }
    
    button.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
}

// ========== 粒子效果 ==========
function createParticles(x, y, color) {
    const particleCount = 25;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        const size = Math.random() * 12 + 4;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.background = color;
        particle.style.borderRadius = '50%';
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.boxShadow = `0 0 ${size * 1.5}px ${color}`;
        
        document.body.appendChild(particle);
        
        const angle = (Math.PI * 2 / particleCount) * i + Math.random() * 0.5;
        const velocity = Math.random() * 120 + 60;
        const vx = Math.cos(angle) * velocity;
        const vy = Math.sin(angle) * velocity;
        
        let posX = x;
        let posY = y;
        let opacity = 1;
        let scale = 1;
        
        const animate = () => {
            posX += vx * 0.018;
            posY += vy * 0.018 + 1.5;
            opacity -= 0.018;
            scale -= 0.01;
            
            particle.style.left = posX + 'px';
            particle.style.top = posY + 'px';
            particle.style.opacity = opacity;
            particle.style.transform = `scale(${Math.max(scale, 0)})`;
            
            if (opacity > 0) {
                requestAnimationFrame(animate);
            } else {
                particle.remove();
            }
        };
        
        requestAnimationFrame(animate);
    }
}

// ========== 场景切换 ==========
function switchScene(fromId, toId) {
    if (isTransitioning) return;
    isTransitioning = true;
    
    const fromScene = document.getElementById(fromId);
    const toScene = document.getElementById(toId);
    
    fromScene.classList.remove('active');
    
    setTimeout(() => {
        toScene.classList.add('active');
        currentScene = toId;
        isTransitioning = false;
    }, 350);
}

// ========== 返回选择页面 ==========
function goBack() {
    if (currentScene === 'scene1' || isTransitioning) return;
    
    playSound('clickSound');
    switchScene(currentScene, 'scene1');
}

// ========== 选择处理 ==========
function makeChoice(choice, event) {
    if (currentScene !== 'scene1' || isTransitioning) return;
    
    playSound('clickSound');
    
    const button = document.getElementById('choice' + choice);
    if (button) {
        createRipple(event || null, button);
        button.classList.add('pressed');
        setTimeout(() => button.classList.remove('pressed'), 150);
    }
    
    setTimeout(() => {
        if (choice === 1) {
            switchScene('scene1', 'scene2');
        } else {
            switchScene('scene1', 'scene3');
        }
    }, 200);
}

// ========== 显示信任值 ==========
function showTrust(value, event) {
    if (isTransitioning) return;
    
    playSound('trustSound');
    
    // 获取当前场景的信任按钮
    const button = currentScene === 'scene2' 
        ? document.getElementById('trust1') 
        : document.getElementById('trust2');
    
    if (button) {
        createRipple(event || null, button);
        button.classList.add('pressed');
        setTimeout(() => button.classList.remove('pressed'), 150);
    }
    
    // 屏幕闪烁
    const flash = document.getElementById('screenFlash');
    flash.classList.add('flash');
    setTimeout(() => flash.classList.remove('flash'), 400);
    
    // 粒子效果 - 从按钮中心发射
    if (button) {
        const rect = button.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        createParticles(centerX, centerY, '#ffd700');
        
        // 额外添加一些白色粒子
        setTimeout(() => {
            createParticles(centerX, centerY, '#ffffff');
        }, 100);
    }
    
    // 信任值弹出
    const popup = document.getElementById('trustPopup');
    popup.textContent = `信任 +${value}`;
    popup.classList.remove('show');
    void popup.offsetWidth;
    popup.classList.add('show');
}

// ========== 键盘控制 ==========
document.addEventListener('keydown', function(e) {
    // 防止重复触发
    if (e.repeat) return;
    
    switch(e.key) {
        case '1':
            if (currentScene === 'scene1') {
                makeChoice(1, null);
            } else if (currentScene === 'scene2') {
                showTrust(10, null);
            } else if (currentScene === 'scene3') {
                showTrust(20, null);
            }
            break;
            
        case '2':
            if (currentScene === 'scene1') {
                makeChoice(2, null);
            }
            break;
            
        case 'Escape':
            goBack();
            break;
            
        case 'Enter':
        case ' ':
            // 在结果页面按回车或空格触发信任按钮
            if (currentScene === 'scene2') {
                showTrust(10, null);
            } else if (currentScene === 'scene3') {
                showTrust(20, null);
            }
            e.preventDefault();
            break;
    }
});

// ========== 页面初始化 ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('剧情选择游戏已加载');
    console.log('按键说明: 1/2 选择选项, ESC 返回, Enter/空格 确认信任');
});
