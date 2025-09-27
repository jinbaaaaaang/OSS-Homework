# This example is not working in Spyder directly (F5 or Run)
# Please type '!python turtle_runaway.py' on IPython console in your Spyder.
import tkinter as tk
import turtle, time, pathlib, math

ASSETS = pathlib.Path(__file__).resolve().parent / "assets"

class RunawayGame: # 전체 게임의 상태, 루프, 판정, HUD 담당하는 컨트롤러 클래스
    def __init__(self, canvas, runner, chaser, catch_radius=50): # 초기화: canvas, 도둑/술래, 잡힘 판정 반경 설정
        self.canvas = canvas # turtle 이벤트/타이머 걸 대상(TurtleScreen 객체)
        self.runner = runner # 도둑 거북이 객체 보관
        self.chaser = chaser # 술래 거북이 객체 보관
        self.catch_radius2 = catch_radius**2 # 반경 제곱

        # Initialize 'runner' and 'chaser'
        self.runner.shape('turtle') # 도둑 거북이 모양
        self.runner.color('blue') # 도둑 색상
        self.runner.penup() # 선 안 그리도록 펜 올리기

        self._tomato_img = tk.PhotoImage(file=str(ASSETS / "tomato.gif"))
        self._tomato_tiny = self._tomato_img.subsample(10, 10)
        self.canvas.register_shape("tomato_tiny", turtle.Shape("image", self._tomato_tiny))

        self.runner.shape("tomato_tiny")

        self.runner2 = RandomMover(canvas)
        self.runner2.penup()
        self.runner2.shape("tomato_tiny")

        self.runner3 = RandomMover(canvas)
        self.runner3.penup()
        self.runner3.shape("tomato_tiny")

        self.chaser.shape('turtle') # 술래 거북이 모양
        self.chaser.color('red') # 술래 색상
        self.chaser.penup() # 선 안 그리도록 펜 올리기

        self._gini_img = tk.PhotoImage(file=str(ASSETS / "gini.gif"))
        self._gini_tiny = self._gini_img.subsample(5, 5)
        self.canvas.register_shape("gini_tiny", turtle.Shape("image", self._gini_tiny))

        self.chaser.shape("gini_tiny")

        # Instantiate another turtle for drawing
        self.drawer = turtle.RawTurtle(canvas) # HUD 텍스트 전용 거북이 생성 (같은 스크린 위에 그리기)
        self.drawer.hideturtle() # 텍스트 전용 거북이는 화면 표시 X (커서 숨김)
        self.drawer.penup() # 선 그리기 비활성화

        self.status = turtle.RawTurtle(canvas)
        self.status.hideturtle()
        self.status.penup()

    def _keep_inside(self, t):
        BX, BY = 340, 340

        x, y = t.pos()
        hitx = (x < -BX) or (x > BX)
        hity = (y < -BY) or (y > BY)

        if not (hitx or hity):
            return
        
        nx = max(-BX, min(BX, x))
        ny = max(-BY, min(BY, y))
        t.setpos(nx, ny)

        h = t.heading()
        if hitx:
            h = (180 - h) % 360
        if hity:
            h = (-h) % 360
        t.setheading(h)

    def is_catched(self): # 잡혔는지 판정
        p = self.runner.pos()
        q = self.chaser.pos()
        dx, dy = p[0] - q[0], p[1] - q[1]
        return dx**2 + dy**2 < self.catch_radius2 # 거리제곱 < 반경제곱 이면 TRUE

    def start(self, init_dist=400, ai_timer_msec=100): # 게임 시작 설정: 초기 배치 / 타이머 주기
        self.runner.setpos((-init_dist / 2, 0)) # 도둑 위치
        self.runner.setheading(0) # 도둑 방향
        self.runner2.setpos((-init_dist/4, +100))
        self.runner2.setheading(0)
        self.runner3.setpos((-init_dist/3, -200))
        self.runner3.setheading(0)

        self.chaser.setpos((+init_dist / 2, 0)) # 술래 위치
        self.chaser.setheading(180) # 술래 방향

        # TODO) You can do something here and follows.
        self._start_time = time.time()
        self._limit_time = 60000
        self._score = 0
        self._prev_catched = False

        self.drawer.penup()
        self.drawer.setpos(-300, 300)
        self.drawer.write(" ")
        
        self.ai_timer_msec = ai_timer_msec # AI/게임 step() 호출할 간격 저장
        self.canvas.ontimer(self.step, self.ai_timer_msec) # 일정 시간 후 step() 호출

    def step(self): # 게임의 한 step: 이동 / 판정 / HUD 갱신 / 다음 호출 예약
        self.runner.run_ai(self.chaser.pos(), self.chaser.heading()) # 도둑 AI 한 step 실행(상대 위치, 방향 참고 가능)
        self.runner2.run_ai(self.chaser.pos(), self.chaser.heading())
        self.runner3.run_ai(self.chaser.pos(), self.chaser.heading())

        self._keep_inside(self.runner)
        self._keep_inside(self.runner2)
        self._keep_inside(self.runner3)

        self.chaser.run_ai(self.runner.pos(), self.runner.heading()) # 술래 AI 한 step 실행
        self._keep_inside(self.chaser)

        # TODO) You can do something here and follows.
        now = time.time()
        elapsed_time = now - self._start_time
        remain_time = self._limit_time/1000.0 - elapsed_time

        def _hit(r):
            old = self.runner
            self.runner = r
            try:
                return self.is_catched()
            finally:
                self.runner = old
        
        hit1 = self.is_catched()
        hit2 = _hit(self.runner2)
        hit3 = _hit(self.runner3)
        any_hit = hit1 or hit2 or hit3 

        if any_hit and not self._prev_catched:
            self._score += 1
        self._prev_catched = any_hit

        is_catched = self.is_catched() # 현재 step에서 잡힘 여부 판단
        self.drawer.undo() # 직전 한 번의 write 되돌림
        self.drawer.penup() # 텍스트 쓰기 준비
        self.drawer.setpos(-300, 290) # HUD 텍스트 위치로 이동
        self.drawer.write("The guinea pig really wants to eat a tomato!!!\n"
                            f"Did the guinea pig eat a tomato? {any_hit}",
                            font=("Arial", 10, "normal")) # 잡힘 여부 화면에 출력

        self.status.clear()
        self.status.setpos(300, 300)
        self.status.write(f"TIME : {max(0.0, remain_time):.0f}s", align="right", font=("Arial", 12, "normal"))
        self.status.setpos(300, 280)
        self.status.write(f"SCORE: {self._score}", align="right", font=("Arial", 12, "normal"))

        if remain_time <= 0:
            self.status.setpos(-300, 260)
            self.status.write("!!!GAME OVER!!!", font=("Arial", 14, "bold"))
            self.status.setpos(-300, 240)
            self.status.write(f"Eaten tomatoes: {self._score}", font=("Arial", 14, "normal"))
            return

        # Note) The following line should be the last of this function to keep the game playing
        self.canvas.ontimer(self.step, self.ai_timer_msec) # 다음 step 다시 예약 (재귀적 타이머 등록으로 게임 지속)

class ManualMover(turtle.RawTurtle): # 수동 조작 거북이: 키보드 이벤트로 이동
    def __init__(self, canvas, step_move=10, step_turn=10): # 이동 / 회전 step 크기 설정
        super().__init__(canvas) # 같은 스크린 위에 RawTurTle 초기화
        self.step_move = step_move # 앞뒤 이동 거리 단위
        self.step_turn = step_turn # 좌우 회전 각도 단위

        # Register event handlers
        canvas.onkeypress(lambda: self.forward(self.step_move), 'Up')
        canvas.onkeypress(lambda: self.backward(self.step_move), 'Down')
        canvas.onkeypress(lambda: self.left(self.step_turn), 'Left')
        canvas.onkeypress(lambda: self.right(self.step_turn), 'Right')
        canvas.listen()

    def run_ai(self, opp_pos, opp_heading): # 수동 조작이라 AI 없음
        pass

class RandomMover(turtle.RawTurtle): # 무작위로 전진/회전하는 AI 거북이
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn

    def run_ai(self, opp_pos, opp_heading): # 한 step 동안의 무작위 동작 정의
        lead = 10
        rad = math.radians(opp_heading)
        predicted = (opp_pos[0] + lead*math.cos(rad), opp_pos[1] + lead*math.sin(rad))
        target = self.towards(predicted)

        away = (target + 180) % 360
        self.setheading(away)  
        self.forward(self.step_move)

if __name__ == '__main__': # 이 파일 직접 실행 시에만 코드 수행
    # Use 'TurtleScreen' instead of 'Screen' to prevent an exception from the singleton 'Screen'
    root = tk.Tk()
    root.title("guinea pig & tomato")
    canvas = tk.Canvas(root, width=700, height=700)
    canvas.pack()
    screen = turtle.TurtleScreen(canvas)

    # TODO) Change the follows to your turtle if necessary
    runner = RandomMover(screen) # 도둑 거북이: 무작위 이동 AI 거북이
    chaser = ManualMover(screen) # 술래 거북이: 키보드 조작 거북이

    screen.addshape(str(ASSETS / "tomato.gif"))
    screen.addshape(str(ASSETS / "gini.gif"))

    game = RunawayGame(screen, runner, chaser) # 게임 컨트롤러 인스턴스 생성

    game.start() # 초기 배치 / 타이머 등록으로 게임 시작
    screen.mainloop()
