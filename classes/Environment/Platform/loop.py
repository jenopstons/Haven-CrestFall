if self._destroyed:
    return
self.dx = 0
self.dy = 0
if _hit_stopped():
    return
if self.springTimer > 0:
    self.springTimer -= 1
    if self.springTimer == 0:
        _apply_pose(self, self.springIdlePose)
        self.scaleX = getattr(self, 'artFacing', 1)
if not self.moving:
    return
# dir=1 means "toward the high end", since the target can be above or
# below start.
if self.axis == 'y':
    prevY = self.y
    lo = min(self.startY, self.targetY)
    hi = max(self.startY, self.targetY)
    if self.dir > 0:
        self.y += self.speed
        if self.y >= hi:
            self.y = hi
            self.dir = -1
    else:
        self.y -= self.speed
        if self.y <= lo:
            self.y = lo
            self.dir = 1
    self.dy = self.y - prevY
    return
prevX = self.x
lo = min(self.startX, self.targetX)
hi = max(self.startX, self.targetX)
if self.dir > 0:
    self.x += self.speed
    if self.x >= hi:
        self.x = hi
        self.dir = -1
else:
    self.x -= self.speed
    if self.x <= lo:
        self.x = lo
        self.dir = 1
self.dx = self.x - prevX
