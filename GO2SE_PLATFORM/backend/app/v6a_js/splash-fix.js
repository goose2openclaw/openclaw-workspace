// 启动动画修复 - 立即执行
(function() {
    console.log('Splash fix starting...');
    
    function initSplash() {
        console.log('Init splash running...');
        const splash = document.getElementById('splash');
        const app = document.getElementById('app');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (!splash) {
            console.log('Splash not found!');
            return;
        }
        
        console.log('Splash found, starting animation...');
        
        const steps = [
            { target: 20, label: '连接后端...' },
            { target: 40, label: '加载配置...' },
            { target: 60, label: '同步双脑...' },
            { target: 80, label: '初始化模块...' },
            { target: 100, label: '启动完成!' }
        ];
        
        let progress = 0;
        
        function updateUI(current, label) {
            if (progressFill) progressFill.style.width = current + '%';
            if (progressText) progressText.textContent = label + ' ' + current + '%';
        }
        
        function animateTo(target, label, duration) {
            return new Promise(resolve => {
                const start = progress;
                const startTime = performance.now();
                function animate(currentTime) {
                    const elapsed = currentTime - startTime;
                    const p = Math.min(elapsed / duration, 1);
                    const current = Math.round(start + (target - start) * p);
                    progress = current;
                    updateUI(current, label);
                    if (p < 1) {
                        requestAnimationFrame(animate);
                    } else {
                        resolve();
                    }
                }
                requestAnimationFrame(animate);
            });
        }
        
        async function run() {
            console.log('Running animation steps...');
            for (const step of steps) {
                await animateTo(step.target, step.label, 300);
                await new Promise(r => setTimeout(r, 200));
            }
            await new Promise(r => setTimeout(r, 300));
            
            console.log('Hiding splash, showing app...');
            splash.classList.add('hidden');
            if (app) {
                app.classList.remove('hidden');
                app.style.display = 'flex';
            }
            setTimeout(() => {
                splash.style.display = 'none';
                splash.style.visibility = 'hidden';
            }, 500);
            
            console.log('Done! App should be visible now.');
        }
        
        run();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSplash);
    } else {
        initSplash();
    }
})();
