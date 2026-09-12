export interface TrackedBehavior {
  num_clicks: number;
  time_on_page: number;
  num_redirects: number;
  failed_logins: number;
  mouse_speed: number;
  typing_speed: number;
  tab_switches: number;
}

class BehaviorTracker {
  private startTime: number;

  private clicks = 0;

  private tabSwitches = 0;

  private mouseDistances: number[] = [];

  private mouseTimes: number[] = [];

  private typingSpeeds: number[] = [];

  private lastMouseX: number | null = null;

  private lastMouseY: number | null = null;

  private lastMouseTime: number | null = null;

  private lastKeyTime: number | null = null;

  private visibilityHandler: () => void;

  private clickHandler: () => void;

  private mouseHandler: (event: MouseEvent) => void;

  private keyHandler: () => void;

  constructor() {
    this.startTime = Date.now();

    this.visibilityHandler =
      this.handleVisibilityChange.bind(this);

    this.clickHandler =
      this.handleClick.bind(this);

    this.mouseHandler =
      this.handleMouseMove.bind(this);

    this.keyHandler =
      this.handleKeyPress.bind(this);

    document.addEventListener(
      "visibilitychange",
      this.visibilityHandler
    );

    document.addEventListener(
      "click",
      this.clickHandler
    );

    document.addEventListener(
      "mousemove",
      this.mouseHandler
    );

    document.addEventListener(
      "keydown",
      this.keyHandler
    );
  }

  private handleClick() {
    this.clicks += 1;
  }

  private handleVisibilityChange() {
    if (document.hidden) {
      this.tabSwitches += 1;
    }
  }

  private handleMouseMove(
    event: MouseEvent
  ) {
    const now = Date.now();

    if (
      this.lastMouseX !== null &&
      this.lastMouseY !== null &&
      this.lastMouseTime !== null
    ) {
      const dx =
        event.clientX -
        this.lastMouseX;

      const dy =
        event.clientY -
        this.lastMouseY;

      const distance = Math.sqrt(
        dx * dx + dy * dy
      );

      const elapsed =
        now -
        this.lastMouseTime;

      if (elapsed > 0) {
        this.mouseDistances.push(
          distance
        );

        this.mouseTimes.push(
          elapsed
        );
      }
    }

    this.lastMouseX =
      event.clientX;

    this.lastMouseY =
      event.clientY;

    this.lastMouseTime =
      now;
  }

  private handleKeyPress() {
    const now = Date.now();

    if (this.lastKeyTime !== null) {
      const elapsed =
        now -
        this.lastKeyTime;

      if (
        elapsed > 0 &&
        elapsed < 5000
      ) {
        const charactersPerSecond =
          1000 / elapsed;

        this.typingSpeeds.push(
          charactersPerSecond
        );
      }
    }

    this.lastKeyTime =
      now;
  }

  private calculateMouseSpeed(): number {
    if (
      this.mouseDistances.length === 0 ||
      this.mouseTimes.length === 0
    ) {
      return 0;
    }

    const totalDistance =
      this.mouseDistances.reduce(
        (sum, value) =>
          sum + value,
        0
      );

    const totalTime =
      this.mouseTimes.reduce(
        (sum, value) =>
          sum + value,
        0
      );

    if (totalTime === 0) {
      return 0;
    }

    return (
      totalDistance /
      (totalTime / 1000)
    );
  }

  private calculateTypingSpeed(): number {
    if (
      this.typingSpeeds.length === 0
    ) {
      return 0;
    }

    const total =
      this.typingSpeeds.reduce(
        (sum, value) =>
          sum + value,
        0
      );

    return (
      total /
      this.typingSpeeds.length
    );
  }

  public getBehavior(): TrackedBehavior {
    const elapsed =
      (Date.now() -
        this.startTime) /
      1000;

    return {
      num_clicks: this.clicks,

      time_on_page: Number(
        elapsed.toFixed(2)
      ),

      num_redirects: 0,

      failed_logins: 0,

      mouse_speed: Number(
        this.calculateMouseSpeed().toFixed(
          2
        )
      ),

      typing_speed: Number(
        this.calculateTypingSpeed().toFixed(
          2
        )
      ),

      tab_switches:
        this.tabSwitches,
    };
  }

  public reset() {
    this.startTime =
      Date.now();

    this.clicks = 0;

    this.tabSwitches = 0;

    this.mouseDistances = [];

    this.mouseTimes = [];

    this.typingSpeeds = [];

    this.lastMouseX = null;

    this.lastMouseY = null;

    this.lastMouseTime = null;

    this.lastKeyTime = null;
  }

  public destroy() {
    document.removeEventListener(
      "visibilitychange",
      this.visibilityHandler
    );

    document.removeEventListener(
      "click",
      this.clickHandler
    );

    document.removeEventListener(
      "mousemove",
      this.mouseHandler
    );

    document.removeEventListener(
      "keydown",
      this.keyHandler
    );
  }
}

export default BehaviorTracker;