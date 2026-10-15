import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird Pro",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Flappy Bird Arcade Edition")
st.caption("Nhấn **Phím cách (Space)** hoặc **Chạm/Click vào màn hình** để đập cánh bay lên.")

flappy_bird_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * {
            box-sizing: border-box;
            user-select: none;
            -webkit-user-select: none;
        }
        body {
            margin: 0;
            padding: 10px 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background: transparent;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        #game-container {
            position: relative;
            box-shadow: 0 12px 28px rgba(0,0,0,0.28);
            border-radius: 16px;
            overflow: hidden;
            border: 4px solid #1a252f;
            display: inline-block;
        }
        canvas {
            display: block;
            background: #4ec0ca;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <canvas id="flappyCanvas" width="360" height="560"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('flappyCanvas');
        const ctx = canvas.getContext('2d');

        // ================= HỆ THỐNG ÂM THANH (WEB AUDIO API) =================
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        let audioCtx = null;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new AudioContext();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        // Âm thanh vỗ cánh (Flap)
        function playFlapSound() {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.type = 'sine';
            const now = audioCtx.currentTime;
            osc.frequency.setValueAtTime(400, now);
            osc.frequency.exponentialRampToValueAtTime(750, now + 0.1);

            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);

            osc.start(now);
            osc.stop(now + 0.1);
        }

        // Âm thanh qua ống ghi điểm (Score)
        function playScoreSound() {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const osc1 = audioCtx.createOscillator();
            const gain1 = audioCtx.createGain();
            osc1.connect(gain1);
            gain1.connect(audioCtx.destination);

            osc1.type = 'triangle';
            osc1.frequency.setValueAtTime(650, now);
            gain1.gain.setValueAtTime(0.18, now);
            gain1.gain.exponentialRampToValueAtTime(0.01, now + 0.12);

            osc1.start(now);
            osc1.stop(now + 0.12);

            const osc2 = audioCtx.createOscillator();
            const gain2 = audioCtx.createGain();
            osc2.connect(gain2);
            gain2.connect(audioCtx.destination);
            osc2.type = 'triangle';
            osc2.frequency.setValueAtTime(980, now + 0.08);
            gain2.gain.setValueAtTime(0.18, now + 0.08);
            gain2.gain.exponentialRampToValueAtTime(0.01, now + 0.22);

            osc2.start(now + 0.08);
            osc2.stop(now + 0.22);
        }

        // Âm thanh va chạm (Hit/Die)
        function playHitSound() {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.type = 'sawtooth';
            const now = audioCtx.currentTime;
            osc.frequency.setValueAtTime(220, now);
            osc.frequency.exponentialRampToValueAtTime(60, now + 0.25);

            gain.gain.setValueAtTime(0.28, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

            osc.start(now);
            osc.stop(now + 0.25);
        }

        // ================= TRẠNG THÁI GAME =================
        let frames = 0;
        let score = 0;
        let highScore = parseInt(localStorage.getItem('flappy_hs') || '0');
        let gameState = 'START'; // 'START', 'PLAYING', 'GAMEOVER'

        // Đám mây nền
        const clouds = [
            { x: 30, y: 70, scale: 1.1, speed: 0.35 },
            { x: 190, y: 110, scale: 0.85, speed: 0.25 },
            { x: 310, y: 60, scale: 1.0, speed: 0.3 }
        ];

        // ================= NHÂN VẬT CHIM =================
        const bird = {
            x: 65,
            y: 200,
            radius: 13,
            gravity: 0.22,     // Trọng lực mượt mà
            jump: 4.6,         // Lực nhảy êm, không giật
            speed: 0,
            rotation: 0,
            wingPhase: 0,

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                
                // Xoay góc nghiêng theo vận tốc rơi/bay
                if (gameState === 'PLAYING') {
                    this.rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 6, (this.speed * 4) * Math.PI / 180));
                } else {
                    this.rotation = 0;
                }
                ctx.rotate(this.rotation);

                // Thân chim (Hình bầu dục vàng)
                ctx.fillStyle = '#ffca28';
                ctx.beginPath();
                ctx.ellipse(0, 0, 15, 12, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.lineWidth = 1.5;
                ctx.strokeStyle = '#d48806';
                ctx.stroke();

                // Bụng chim (vàng nhạt)
                ctx.fillStyle = '#fff9c4';
                ctx.beginPath();
                ctx.ellipse(-2, 4, 9, 6, 0, 0, Math.PI * 2);
                ctx.fill();

                // Cánh chim đập theo nhịp
                this.wingPhase += (gameState === 'PLAYING' ? 0.25 : 0.12);
                const wingY = Math.sin(this.wingPhase) * 4;
                ctx.fillStyle = '#fbc02d';
                ctx.beginPath();
                ctx.ellipse(-6, wingY, 7, 4.5, -0.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#b78103';
                ctx.stroke();

                // Mắt to kiểu hoạt hình
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(6, -4, 4.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 1;
                ctx.stroke();

                // Con ngươi
                ctx.fillStyle = '#111111';
                ctx.beginPath();
                ctx.arc(8, -4, 2.2, 0, Math.PI * 2);
                ctx.fill();
                // Ánh sáng mắt
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(9, -5, 1, 0, Math.PI * 2);
                ctx.fill();

                // Mỏ chim
                ctx.fillStyle = '#ff7043';
                ctx.beginPath();
                ctx.moveTo(11, -2);
                ctx.lineTo(19, 1);
                ctx.lineTo(11, 4);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = '#d84315';
                ctx.stroke();

                ctx.restore();
            },

            flap() {
                this.speed = -this.jump;
                playFlapSound();
            },

            update() {
                if (gameState === 'START') {
                    // Hiệu ứng bay bồng bềnh ở màn hình chờ
                    this.y = 210 + Math.sin(frames * 0.08) * 6;
                    this.speed = 0;
                } else if (gameState === 'PLAYING') {
                    this.speed += this.gravity;
                    this.y += this.speed;

                    // Chạm mặt đất
                    if (this.y + this.radius >= canvas.height - 70) {
                        this.y = canvas.height - 70 - this.radius;
                        triggerGameOver();
                    }

                    // Chạm nóc trần
                    if (this.y - this.radius <= 0) {
                        this.y = this.radius;
                        this.speed = 0;
                    }
                } else if (gameState === 'GAMEOVER') {
                    // Rơi tự do khi thua
                    if (this.y + this.radius < canvas.height - 70) {
                        this.speed += this.gravity * 1.5;
                        this.y += this.speed;
                    }
                }
            },

            reset() {
                this.y = 200;
                this.speed = 0;
                this.rotation = 0;
            }
        };

        // ================= CỘT ỐNG (PIPES) =================
        const pipes = {
            position: [],
            gap: 135,         // Khoảng cách thoáng hơn giúp dễ luồn qua
            w: 56,
            dx: 1.85,         // Tốc độ lướt ổn định, dễ phản xạ

            draw() {
                for (let i = 0; i < this.position.length; i++) {
                    const p = this.position[i];
                    const topY = p.y;
                    const bottomY = p.y + this.gap;

                    // Vẽ Ống Trên
                    this.renderSinglePipe(p.x, 0, this.w, topY, true);

                    // Vẽ Ống Dưới
                    const bottomHeight = canvas.height - 70 - bottomY;
                    this.renderSinglePipe(p.x, bottomY, this.w, bottomHeight, false);
                }
            },

            renderSinglePipe(x, y, w, h, isTop) {
                // Gradient thân ống màu xanh Mario
                const grad = ctx.createLinearGradient(x, 0, x + w, 0);
                grad.addColorStop(0, '#55bb32');
                grad.addColorStop(0.3, '#79d749');
                grad.addColorStop(0.7, '#4fa92b');
                grad.addColorStop(1, '#2f6d19');

                ctx.fillStyle = grad;
                ctx.fillRect(x, y, w, h);
                ctx.strokeStyle = '#1d480f';
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, w, h);

                // Gờ vành ống
                const lipH = 22;
                const lipW = w + 8;
                const lipX = x - 4;
                const lipY = isTop ? (y + h - lipH) : y;

                const lipGrad = ctx.createLinearGradient(lipX, 0, lipX + lipW, 0);
                lipGrad.addColorStop(0, '#66ca3f');
                lipGrad.addColorStop(0.4, '#8aeb57');
                lipGrad.addColorStop(1, '#296515');

                ctx.fillStyle = lipGrad;
                ctx.fillRect(lipX, lipY, lipW, lipH);
                ctx.strokeRect(lipX, lipY, lipW, lipH);
            },

            update() {
                if (gameState !== 'PLAYING') return;

                // Thêm ống mới mỗi 115 frames
                if (frames % 115 === 0) {
                    const minTop = 60;
                    const maxTop = canvas.height - 70 - this.gap - 80;
                    const randomY = Math.floor(Math.random() * (maxTop - minTop)) + minTop;
                    this.position.push({
                        x: canvas.width,
                        y: randomY,
                        passed: false
                    });
                }

                for (let i = 0; i < this.position.length; i++) {
                    const p = this.position[i];
                    p.x -= this.dx;

                    // Tính điểm khi bay qua an toàn
                    if (!p.passed && p.x + this.w < bird.x - bird.radius) {
                        score++;
                        playScoreSound();
                        p.passed = true;
                    }

                    // Kiểm tra va chạm hộp (AABB)
                    const bR = bird.x + bird.radius - 3;
                    const bL = bird.x - bird.radius + 3;
                    const bT = bird.y - bird.radius + 3;
                    const bB = bird.y + bird.radius - 3;

                    if (bR > p.x && bL < p.x + this.w) {
                        if (bT < p.y || bB > p.y + this.gap) {
                            playHitSound();
                            triggerGameOver();
                        }
                    }

                    // Hủy ống khi ra khỏi màn hình bên trái
                    if (p.x + this.w < -10) {
                        this.position.shift();
                        i--;
                    }
                }
            },

            reset() {
                this.position = [];
            }
        };

        // ================= ĐỒ HỌA MÔI TRƯỜNG =================
        function drawSkyAndScenery() {
            // Nền trời chuyển màu
            const skyGrad = ctx.createLinearGradient(0, 0, 0, canvas.height - 70);
            skyGrad.addColorStop(0, '#38a3d3');
            skyGrad.addColorStop(0.7, '#7cd9e6');
            skyGrad.addColorStop(1, '#d8f5f8');
            ctx.fillStyle = skyGrad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Vẽ các đám mây
            ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
            clouds.forEach(c => {
                c.x -= c.speed;
                if (c.x < -80) c.x = canvas.width + 40;

                ctx.beginPath();
                ctx.arc(c.x, c.y, 22 * c.scale, 0, Math.PI * 2);
                ctx.arc(c.x + 20 * c.scale, c.y - 10 * c.scale, 26 * c.scale, 0, Math.PI * 2);
                ctx.arc(c.x + 45 * c.scale, c.y, 20 * c.scale, 0, Math.PI * 2);
                ctx.fill();
            });

            // Dãy núi/cây phía xa
            ctx.fillStyle = '#9fe08b';
            ctx.beginPath();
            ctx.moveTo(0, canvas.height - 70);
            for (let i = 0; i <= canvas.width + 40; i += 50) {
                ctx.quadraticCurveTo(i + 25, canvas.height - 110, i + 50, canvas.height - 70);
            }
            ctx.fill();
        }

        // Vẽ sàn đất chuyển động
        let groundOffset = 0;
        function drawGround() {
            const gy = canvas.height - 70;
            if (gameState === 'PLAYING') {
                groundOffset = (groundOffset + 1.85) % 18;
            }

            // Đất
            ctx.fillStyle = '#ded895';
            ctx.fillRect(0, gy, canvas.width, 70);

            // Cỏ xanh trên mặt đất
            ctx.fillStyle = '#73bf2e';
            ctx.fillRect(0, gy, canvas.width, 14);
            ctx.fillStyle = '#599c22';
            ctx.fillRect(0, gy + 12, canvas.width, 4);

            // Vạch hoa văn sọc xiên chuyển động trên nền đất
            ctx.fillStyle = '#c5be74';
            for (let x = -20 - groundOffset; x < canvas.width + 20; x += 18) {
                ctx.beginPath();
                ctx.moveTo(x, gy + 16);
                ctx.lineTo(x + 9, gy + 16);
                ctx.lineTo(x + 2, gy + 70);
                ctx.lineTo(x - 7, gy + 70);
                ctx.closePath();
                ctx.fill();
            }
        }

        // ================= GIAO DIỆN & BẢNG ĐIỂM =================
        function drawUI() {
            if (gameState === 'PLAYING') {
                // Điểm số phong cách viền bóng to giữa màn hình
                ctx.fillStyle = '#ffffff';
                ctx.font = '900 38px Arial';
                ctx.textAlign = 'center';
                ctx.shadowColor = 'rgba(0,0,0,0.4)';
                ctx.shadowBlur = 6;
                ctx.shadowOffsetX = 2;
                ctx.shadowOffsetY = 2;
                ctx.fillText(score, canvas.width / 2, 60);

                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 2.5;
                ctx.strokeText(score, canvas.width / 2, 60);
                resetShadow();
            } else if (gameState === 'START') {
                ctx.fillStyle = '#ffffff';
                ctx.font = '900 32px Arial';
                ctx.textAlign = 'center';
                drawTextWithOutline('FLAPPY BIRD', canvas.width / 2, 170, '#ffffff', '#2c3e50', 3);

                // Nút / Hướng dẫn
                drawCard(canvas.width / 2 - 120, 260, 240, 110, 'rgba(0,0,0,0.4)');
                ctx.font = 'bold 16px Arial';
                ctx.fillStyle = '#ffffff';
                ctx.fillText('Nhấn SPACE hoặc CLICK', canvas.width / 2, 305);
                ctx.font = '14px Arial';
                ctx.fillStyle = '#ffeaa7';
                ctx.fillText('để vỗ cánh & bật âm thanh', canvas.width / 2, 335);
            } else if (gameState === 'GAMEOVER') {
                // Màn mờ đen nhẹ
                ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Chữ Game Over
                drawTextWithOutline('GAME OVER', canvas.width / 2, 160, '#ff4757', '#2f3542', 4);

                // Bảng hiển thị kết quả (Score Board)
                const bx = canvas.width / 2 - 130;
                const by = 195;
                drawCard(bx, by, 260, 150, '#eccc68');
                ctx.strokeStyle = '#b89430';
                ctx.lineWidth = 3;
                ctx.strokeRect(bx, by, 260, 150);

                // Huy chương
                drawMedal(bx + 45, by + 75);

                // Điểm hiện tại & Kỷ lục
                ctx.textAlign = 'right';
                ctx.font = 'bold 15px Arial';
                ctx.fillStyle = '#57606f';
                ctx.fillText('ĐIỂM SỐ', bx + 240, by + 45);
                ctx.font = 'bold 24px Arial';
                ctx.fillStyle = '#2f3542';
                ctx.fillText(score, bx + 240, by + 75);

                ctx.font = 'bold 15px Arial';
                ctx.fillStyle = '#57606f';
                ctx.fillText('KỶ LỤC', bx + 240, by + 105);
                ctx.font = 'bold 24px Arial';
                ctx.fillStyle = '#d63031';
                ctx.fillText(highScore, bx + 240, by + 135);

                // Nút chơi lại
                ctx.textAlign = 'center';
                ctx.font = 'bold 16px Arial';
                drawTextWithOutline('Click để Chơi Lại', canvas.width / 2, 380, '#ffffff', '#2f3542', 2);
            }
        }

        function drawCard(x, y, w, h, fill) {
            ctx.fillStyle = fill;
            ctx.beginPath();
            ctx.roundRect ? ctx.roundRect(x, y, w, h, 14) : ctx.rect(x, y, w, h);
            ctx.fill();
        }

        function drawMedal(x, y) {
            let color = '#a4b0be'; // Đồng
            let border = '#747d8c';
            if (score >= 20) {
                color = '#ffa502'; // Vàng
                border = '#e58e26';
            } else if (score >= 10) {
                color = '#ced6e0'; // Bạc
                border = '#a4b0be';
            }

            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y, 24, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = border;
            ctx.lineWidth = 3;
            ctx.stroke();

            // Sao ở giữa
            ctx.fillStyle = '#ffffff';
            ctx.font = '18px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('★', x, y + 6);
        }

        function drawTextWithOutline(text, x, y, fill, stroke, strokeW) {
            ctx.font = '900 32px Arial';
            ctx.strokeStyle = stroke;
            ctx.lineWidth = strokeW;
            ctx.strokeText(text, x, y);
            ctx.fillStyle = fill;
            ctx.fillText(text, x, y);
        }

        function resetShadow() {
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 0;
        }

        // ================= ĐIỀU KHIỂN & VÒNG LẶP =================
        function triggerGameOver() {
            if (gameState === 'GAMEOVER') return;
            gameState = 'GAMEOVER';
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('flappy_hs', highScore);
            }
        }

        function handleAction() {
            initAudio(); // Kích hoạt Web Audio ngay khi có tương tác người dùng

            if (gameState === 'START') {
                gameState = 'PLAYING';
                bird.flap();
            } else if (gameState === 'PLAYING') {
                bird.flap();
            } else if (gameState === 'GAMEOVER') {
                // Đợi chim rơi xuống đất mới cho reset
                if (bird.y + bird.radius >= canvas.height - 75) {
                    pipes.reset();
                    bird.reset();
                    score = 0;
                    frames = 0;
                    gameState = 'PLAYING';
                    bird.flap();
                }
            }
        }

        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                handleAction();
            }
        });

        canvas.addEventListener('pointerdown', (e) => {
            e.preventDefault();
            handleAction();
        });

        // Game Loop
        function loop() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            drawSkyAndScenery();
            pipes.update();
            pipes.draw();
            drawGround();
            bird.update();
            bird.draw();
            drawUI();

            frames++;
            requestAnimationFrame(loop);
        }

        loop();
    </script>
</body>
</html>
"""

components.html(flappy_bird_code, height=600)
