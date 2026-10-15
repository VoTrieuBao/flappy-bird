import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird Streamlit",
    page_icon="🐦",
    layout="centered"
)

st.title("🐦 Flappy Bird trên Streamlit")
st.caption("Nhấn **Phím cách (Space)** hoặc **Chạm/Click vào màn hình** để chim đập cánh bay lên.")

flappy_bird_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: transparent;
            font-family: Arial, sans-serif;
            user-select: none;
        }
        canvas {
            border: 3px solid #2c3e50;
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            background-color: #70c5ce;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <canvas id="flappyCanvas" width="360" height="520"></canvas>

    <script>
        const canvas = document.getElementById('flappyCanvas');
        const ctx = canvas.getContext('2d');

        // Biến trạng thái trò chơi
        let frames = 0;
        let score = 0;
        let highScore = 0;
        let gameState = 'START'; // START, PLAYING, GAMEOVER

        // Đối tượng Chim
        const bird = {
            x: 50,
            y: 150,
            w: 24,
            h: 24,
            radius: 12,
            gravity: 0.28,
            jump: 4.8,
            speed: 0,
            
            draw() {
                ctx.fillStyle = '#f1c40f';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#d68910';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Mắt
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(this.x + 5, this.y - 4, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(this.x + 6, this.y - 4, 2, 0, Math.PI * 2);
                ctx.fill();

                // Mỏ
                ctx.fillStyle = '#e67e22';
                ctx.beginPath();
                ctx.moveTo(this.x + 8, this.y - 2);
                ctx.lineTo(this.x + 16, this.y + 2);
                ctx.lineTo(this.x + 8, this.y + 5);
                ctx.closePath();
                ctx.fill();
            },
            
            flap() {
                this.speed = -this.jump;
            },
            
            update() {
                if (gameState === 'START') {
                    this.y = 150 + Math.sin(frames * 0.1) * 5;
                    this.speed = 0;
                } else if (gameState === 'PLAYING') {
                    this.speed += this.gravity;
                    this.y += this.speed;

                    // Va chạm mặt đất
                    if (this.y + this.radius >= canvas.height - 40) {
                        this.y = canvas.height - 40 - this.radius;
                        gameOver();
                    }

                    // Chạm trần
                    if (this.y - this.radius <= 0) {
                        this.y = this.radius;
                        this.speed = 0;
                    }
                }
            },
            
            reset() {
                this.y = 150;
                this.speed = 0;
            }
        };

        // Đối tượng Ống cản
        const pipes = {
            position: [],
            gap: 125,
            w: 52,
            dx: 2,
            
            draw() {
                for (let i = 0; i < this.position.length; i++) {
                    let p = this.position[i];
                    let topY = p.y;
                    let bottomY = p.y + this.gap;

                    // Ống trên
                    ctx.fillStyle = '#2ecc71';
                    ctx.fillRect(p.x, 0, this.w, topY);
                    ctx.strokeStyle = '#27ae60';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(p.x, 0, this.w, topY);

                    // Gờ ống trên
                    ctx.fillRect(p.x - 3, topY - 18, this.w + 6, 18);
                    ctx.strokeRect(p.x - 3, topY - 18, this.w + 6, 18);

                    // Ống dưới
                    let bottomHeight = canvas.height - 40 - bottomY;
                    ctx.fillRect(p.x, bottomY, this.w, bottomHeight);
                    ctx.strokeRect(p.x, bottomY, this.w, bottomHeight);

                    // Gờ ống dưới
                    ctx.fillRect(p.x - 3, bottomY, this.w + 6, 18);
                    ctx.strokeRect(p.x - 3, bottomY, this.w + 6, 18);
                }
            },
            
            update() {
                if (gameState !== 'PLAYING') return;

                // Thêm ống mới mỗi 110 frame
                if (frames % 110 === 0) {
                    let maxTop = canvas.height - 40 - this.gap - 60;
                    let topPipeHeight = Math.floor(Math.random() * (maxTop - 60)) + 60;
                    this.position.push({
                        x: canvas.width,
                        y: topPipeHeight,
                        passed: false
                    });
                }

                for (let i = 0; i < this.position.length; i++) {
                    let p = this.position[i];
                    p.x -= this.dx;

                    // Kiểm tra tính điểm
                    if (!p.passed && p.x + this.w < bird.x - bird.radius) {
                        score++;
                        p.passed = true;
                    }

                    // Xử lý va chạm
                    let birdRight = bird.x + bird.radius - 3;
                    let birdLeft = bird.x - bird.radius + 3;
                    let birdTop = bird.y - bird.radius + 3;
                    let birdBottom = bird.y + bird.radius - 3;

                    if (birdRight > p.x && birdLeft < p.x + this.w) {
                        if (birdTop < p.y || birdBottom > p.y + this.gap) {
                            gameOver();
                        }
                    }

                    // Xóa ống khỏi màn hình
                    if (p.x + this.w <= 0) {
                        this.position.shift();
                        i--;
                    }
                }
            },
            
            reset() {
                this.position = [];
            }
        };

        // Vẽ mặt đất
        function drawGround() {
            ctx.fillStyle = '#ded895';
            ctx.fillRect(0, canvas.height - 40, canvas.width, 40);
            ctx.fillStyle = '#73bf2e';
            ctx.fillRect(0, canvas.height - 40, canvas.width, 8);
        }

        // Vẽ giao diện điểm & thông báo
        function drawUI() {
            if (gameState === 'PLAYING') {
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 32px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(score, canvas.width / 2, 50);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 1.5;
                ctx.strokeText(score, canvas.width / 2, 50);
            } else if (gameState === 'START') {
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 24px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('FLAPPY BIRD', canvas.width / 2, 220);

                ctx.font = '16px Arial';
                ctx.fillText('Nhấp chuột hoặc phím Space', canvas.width / 2, 260);
                ctx.fillText('để bắt đầu', canvas.width / 2, 285);
            } else if (gameState === 'GAMEOVER') {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#e74c3c';
                ctx.font = 'bold 30px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width / 2, 200);

                ctx.fillStyle = '#ffffff';
                ctx.font = '20px Arial';
                ctx.fillText('Điểm: ' + score, canvas.width / 2, 245);
                ctx.fillText('Kỷ lục: ' + highScore, canvas.width / 2, 275);

                ctx.font = '15px Arial';
                ctx.fillText('Nhấp chuột để chơi lại', canvas.width / 2, 320);
            }
        }

        function gameOver() {
            gameState = 'GAMEOVER';
            if (score > highScore) {
                highScore = score;
            }
        }

        function action() {
            if (gameState === 'START') {
                gameState = 'PLAYING';
                bird.flap();
            } else if (gameState === 'PLAYING') {
                bird.flap();
            } else if (gameState === 'GAMEOVER') {
                pipes.reset();
                bird.reset();
                score = 0;
                frames = 0;
                gameState = 'PLAYING';
            }
        }

        // Bắt sự kiện bàn phím & chuột
        window.addEventListener('keydown', function(e) {
            if (e.code === 'Space') {
                e.preventDefault();
                action();
            }
        });

        canvas.addEventListener('click', function(e) {
            action();
        });

        // Game Loop
        function loop() {
            // Xóa khung hình
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Cập nhật tọa độ
            bird.update();
            pipes.update();

            // Vẽ đối tượng
            pipes.draw();
            drawGround();
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

components.html(flappy_bird_code, height=540)
