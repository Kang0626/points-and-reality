var __defProp = Object.defineProperty;
var __typeError = (msg) => {
  throw TypeError(msg);
};
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
var __accessCheck = (obj, member, msg) => member.has(obj) || __typeError("Cannot " + msg);
var __privateGet = (obj, member, getter) => (__accessCheck(obj, member, "read from private field"), getter ? getter.call(obj) : member.get(obj));
var __privateAdd = (obj, member, value) => member.has(obj) ? __typeError("Cannot add the same private member more than once") : member instanceof WeakSet ? member.add(obj) : member.set(obj, value);
var __privateSet = (obj, member, value, setter) => (__accessCheck(obj, member, "write to private field"), setter ? setter.call(obj, value) : member.set(obj, value), value);
var __privateMethod = (obj, member, method) => (__accessCheck(obj, member, "access private method"), method);
var _camera, _element, _pointers, _keys, _orbitCenter, _initialTabIndex, _initialTouchAction, _lastTime, _wheelDelta, _capsLock, _altKey, _moving, _rotating, _panning, _orbiting, _disposed, _onPointerDown, _onPointerMove, _onPointerUp, _onContextMenu, _onWheel, _onKeyDown, _onKeyUp, _onBlur, _CameraControl_instances, updatePointers_fn, updateKeyboard_fn, updateWheel_fn, rotateByPixels_fn, orbitByPixels_fn, panByPixels_fn, moveAlongView_fn, getSpeedMultiplier_fn, getPointerMode_fn, isOrbitModifierActive_fn, getOrbitDistance_fn;
const DEFAULT_OPTIONS = {
  enabled: true,
  keyboardEnabled: true,
  pointerEnabled: true,
  orbitEnabled: true,
  useOrbit: false,
  orbitCenter: { x: 0, y: 0, z: 0 },
  orbitMinDistance: 0.01,
  orbitMaxDistance: 100,
  groundLock: false,
  moveSpeed: 0.4,
  lookSpeed: 4e-3,
  wheelSpeed: 6e-3,
  panSpeed: 6e-3,
  rollSpeed: 1,
  ctrlMultiplier: 2,
  shiftMultiplier: 10,
  capsMultiplier: 20
};
const KEYBOARD_CONTROL_KEYS = /* @__PURE__ */ new Set([
  "KeyW",
  "KeyA",
  "KeyS",
  "KeyD",
  "KeyQ",
  "KeyE",
  "KeyR",
  "KeyF",
  "ShiftLeft",
  "ShiftRight",
  "ControlLeft",
  "ControlRight",
  "AltLeft",
  "AltRight",
  "CapsLock"
]);
const MAX_PITCH = Math.PI / 2 - 1e-3;
const EPSILON = 1e-6;
const DEFAULT_UP = { x: 0, y: 1, z: 0 };
const DEFAULT_ORBIT_CENTER = { x: 0, y: 0, z: 0 };
class CameraControl {
  constructor(camera, element, options = {}) {
    __privateAdd(this, _CameraControl_instances);
    __publicField(this, "enabled");
    __publicField(this, "keyboardEnabled");
    __publicField(this, "pointerEnabled");
    __publicField(this, "orbitEnabled");
    __publicField(this, "useOrbit");
    __publicField(this, "orbitMinDistance");
    __publicField(this, "moveSpeed");
    __publicField(this, "lookSpeed");
    __publicField(this, "wheelSpeed");
    __publicField(this, "panSpeed");
    __publicField(this, "rollSpeed");
    __publicField(this, "shiftMultiplier");
    __publicField(this, "ctrlMultiplier");
    __publicField(this, "capsMultiplier");
    __privateAdd(this, _camera);
    __privateAdd(this, _element);
    __privateAdd(this, _pointers, /* @__PURE__ */ new Map());
    __privateAdd(this, _keys, /* @__PURE__ */ new Set());
    __privateAdd(this, _orbitCenter, copyVector(DEFAULT_ORBIT_CENTER));
    __privateAdd(this, _initialTabIndex);
    __privateAdd(this, _initialTouchAction);
    __privateAdd(this, _lastTime, 0);
    __privateAdd(this, _wheelDelta, 0);
    __privateAdd(this, _capsLock, false);
    __privateAdd(this, _altKey, false);
    __privateAdd(this, _moving, false);
    __privateAdd(this, _rotating, false);
    __privateAdd(this, _panning, false);
    __privateAdd(this, _orbiting, false);
    __privateAdd(this, _disposed, false);
    __privateAdd(this, _onPointerDown, (event) => {
      if (!this.enabled || !this.pointerEnabled) {
        return;
      }
      __privateGet(this, _element).focus({ preventScroll: true });
      __privateSet(this, _altKey, event.altKey);
      __privateGet(this, _pointers).set(event.pointerId, {
        pointerId: event.pointerId,
        pointerType: event.pointerType,
        button: event.button,
        mode: __privateMethod(this, _CameraControl_instances, getPointerMode_fn).call(this, event.pointerType, event.button),
        lastX: event.clientX,
        lastY: event.clientY,
        x: event.clientX,
        y: event.clientY
      });
      __privateGet(this, _element).setPointerCapture(event.pointerId);
      event.preventDefault();
    });
    __privateAdd(this, _onPointerMove, (event) => {
      const pointer = __privateGet(this, _pointers).get(event.pointerId);
      if (!pointer) {
        return;
      }
      __privateSet(this, _altKey, event.altKey);
      pointer.x = event.clientX;
      pointer.y = event.clientY;
      event.preventDefault();
    });
    __privateAdd(this, _onPointerUp, (event) => {
      if (__privateGet(this, _pointers).has(event.pointerId)) {
        __privateGet(this, _pointers).delete(event.pointerId);
        if (__privateGet(this, _element).hasPointerCapture(event.pointerId)) {
          __privateGet(this, _element).releasePointerCapture(event.pointerId);
        }
        if (__privateGet(this, _pointers).size === 0) {
          __privateSet(this, _rotating, false);
          __privateSet(this, _panning, false);
          __privateSet(this, _orbiting, false);
        }
      }
    });
    __privateAdd(this, _onContextMenu, (event) => {
      event.preventDefault();
    });
    __privateAdd(this, _onWheel, (event) => {
      if (!this.enabled || !this.pointerEnabled) {
        return;
      }
      __privateSet(this, _wheelDelta, __privateGet(this, _wheelDelta) + event.deltaY);
      event.preventDefault();
    });
    __privateAdd(this, _onKeyDown, (event) => {
      if (!this.enabled || !this.keyboardEnabled || !KEYBOARD_CONTROL_KEYS.has(event.code)) {
        return;
      }
      __privateGet(this, _keys).add(event.code);
      __privateSet(this, _capsLock, event.getModifierState("CapsLock"));
      __privateSet(this, _altKey, event.altKey || event.code === "AltLeft" || event.code === "AltRight");
      event.preventDefault();
    });
    __privateAdd(this, _onKeyUp, (event) => {
      __privateGet(this, _keys).delete(event.code);
      __privateSet(this, _capsLock, event.getModifierState("CapsLock"));
      __privateSet(this, _altKey, event.altKey);
    });
    __privateAdd(this, _onBlur, () => {
      this.stop();
    });
    __privateSet(this, _camera, camera);
    __privateSet(this, _element, element);
    __privateSet(this, _initialTabIndex, element.getAttribute("tabindex"));
    __privateSet(this, _initialTouchAction, element.style.touchAction);
    const resolved = {
      ...DEFAULT_OPTIONS,
      ...options
    };
    this.enabled = resolved.enabled;
    this.keyboardEnabled = resolved.keyboardEnabled;
    this.pointerEnabled = resolved.pointerEnabled;
    this.orbitEnabled = resolved.orbitEnabled;
    this.useOrbit = resolved.useOrbit;
    this.orbitMinDistance = Math.max(EPSILON, resolved.orbitMinDistance);
    this.orbitMaxDistance = resolved.orbitMaxDistance ?? 100;
    this.groundLock = !!resolved.groundLock;
    this.setOrbitCenter(resolved.orbitCenter);
    this.moveSpeed = resolved.moveSpeed;
    this.lookSpeed = resolved.lookSpeed;
    this.wheelSpeed = resolved.wheelSpeed;
    this.panSpeed = resolved.panSpeed;
    this.rollSpeed = resolved.rollSpeed;
    this.shiftMultiplier = resolved.shiftMultiplier;
    this.ctrlMultiplier = resolved.ctrlMultiplier;
    this.capsMultiplier = resolved.capsMultiplier;
    if (__privateGet(this, _initialTabIndex) === null) {
      element.tabIndex = 0;
    }
    element.style.touchAction = "none";
    element.addEventListener("pointerdown", __privateGet(this, _onPointerDown));
    element.addEventListener("pointermove", __privateGet(this, _onPointerMove));
    element.addEventListener("pointerup", __privateGet(this, _onPointerUp));
    element.addEventListener("pointercancel", __privateGet(this, _onPointerUp));
    element.addEventListener("contextmenu", __privateGet(this, _onContextMenu));
    element.addEventListener("wheel", __privateGet(this, _onWheel), { passive: false });
    element.addEventListener("keydown", __privateGet(this, _onKeyDown));
    element.addEventListener("keyup", __privateGet(this, _onKeyUp));
    window.addEventListener("keyup", __privateGet(this, _onKeyUp));
    window.addEventListener("blur", __privateGet(this, _onBlur));
  }
  setOptions(options) {
    const { orbitCenter, ...rest } = options;
    if (orbitCenter !== void 0) {
      this.setOrbitCenter(orbitCenter);
    }
    for (const [key, value] of Object.entries(rest)) {
      if (value !== void 0) {
        if (key === "orbitMinDistance" && typeof value === "number") {
          this.orbitMinDistance = Math.max(EPSILON, value);
        } else if (key === "orbitMaxDistance" && typeof value === "number") {
          this.orbitMaxDistance = value;
        } else if (key === "groundLock") {
          this.groundLock = !!value;
        } else {
          this[key] = value;
        }
      }
    }
  }
  setOrbitCenter(center) {
    __privateGet(this, _orbitCenter).x = center.x;
    __privateGet(this, _orbitCenter).y = center.y;
    __privateGet(this, _orbitCenter).z = center.z;
  }
  stop() {
    for (const pointer of __privateGet(this, _pointers).values()) {
      if (__privateGet(this, _element).hasPointerCapture(pointer.pointerId)) {
        __privateGet(this, _element).releasePointerCapture(pointer.pointerId);
      }
    }
    __privateGet(this, _keys).clear();
    __privateGet(this, _pointers).clear();
    __privateSet(this, _wheelDelta, 0);
    __privateSet(this, _altKey, false);
    __privateSet(this, _moving, false);
    __privateSet(this, _rotating, false);
    __privateSet(this, _panning, false);
    __privateSet(this, _orbiting, false);
  }
  update(deltaSeconds) {
    if (__privateGet(this, _disposed) || !this.enabled) {
      return false;
    }
    const now = performance.now();
    const delta = deltaSeconds ?? Math.min((now - (__privateGet(this, _lastTime) || now)) / 1e3, 0.1);
    __privateSet(this, _lastTime, now);
    const pointerChanged = this.pointerEnabled ? __privateMethod(this, _CameraControl_instances, updatePointers_fn).call(this) : false;
    const keyboardChanged = this.keyboardEnabled ? __privateMethod(this, _CameraControl_instances, updateKeyboard_fn).call(this, delta) : false;
    const wheelChanged = this.pointerEnabled ? __privateMethod(this, _CameraControl_instances, updateWheel_fn).call(this) : false;
    return pointerChanged || keyboardChanged || wheelChanged;
  }
  getState() {
    const position = __privateGet(this, _camera).position;
    const rotation = __privateGet(this, _camera).rotation;
    const touching = Array.from(__privateGet(this, _pointers).values()).some((pointer) => pointer.pointerType === "touch");
    const interacting = __privateGet(this, _moving) || __privateGet(this, _rotating) || __privateGet(this, _panning) || __privateGet(this, _orbiting) || __privateGet(this, _pointers).size > 0;
    return {
      position: { x: position.x, y: position.y, z: position.z },
      rotation: { x: rotation.x, y: rotation.y, z: rotation.z },
      moving: __privateGet(this, _moving),
      rotating: __privateGet(this, _rotating),
      panning: __privateGet(this, _panning),
      orbiting: __privateGet(this, _orbiting),
      touching,
      interacting,
      speedMultiplier: __privateMethod(this, _CameraControl_instances, getSpeedMultiplier_fn).call(this),
      activePointers: __privateGet(this, _pointers).size,
      orbitCenter: copyVector(__privateGet(this, _orbitCenter)),
      orbitDistance: __privateMethod(this, _CameraControl_instances, getOrbitDistance_fn).call(this)
    };
  }
  orbit(yawDelta, pitchDelta) {
    return orbitCamera(
      __privateGet(this, _camera),
      __privateGet(this, _orbitCenter),
      yawDelta,
      pitchDelta,
      this.orbitMinDistance,
      this.orbitMaxDistance,
      this.groundLock
    );
  }
  dispose() {
    if (__privateGet(this, _disposed)) {
      return;
    }
    this.stop();
    __privateSet(this, _disposed, true);
    __privateGet(this, _element).removeEventListener("pointerdown", __privateGet(this, _onPointerDown));
    __privateGet(this, _element).removeEventListener("pointermove", __privateGet(this, _onPointerMove));
    __privateGet(this, _element).removeEventListener("pointerup", __privateGet(this, _onPointerUp));
    __privateGet(this, _element).removeEventListener("pointercancel", __privateGet(this, _onPointerUp));
    __privateGet(this, _element).removeEventListener("contextmenu", __privateGet(this, _onContextMenu));
    __privateGet(this, _element).removeEventListener("wheel", __privateGet(this, _onWheel));
    __privateGet(this, _element).removeEventListener("keydown", __privateGet(this, _onKeyDown));
    __privateGet(this, _element).removeEventListener("keyup", __privateGet(this, _onKeyUp));
    window.removeEventListener("keyup", __privateGet(this, _onKeyUp));
    window.removeEventListener("blur", __privateGet(this, _onBlur));
    __privateGet(this, _element).style.touchAction = __privateGet(this, _initialTouchAction);
    if (__privateGet(this, _initialTabIndex) === null) {
      __privateGet(this, _element).removeAttribute("tabindex");
    } else {
      __privateGet(this, _element).setAttribute("tabindex", __privateGet(this, _initialTabIndex));
    }
  }
}
_camera = new WeakMap();
_element = new WeakMap();
_pointers = new WeakMap();
_keys = new WeakMap();
_orbitCenter = new WeakMap();
_initialTabIndex = new WeakMap();
_initialTouchAction = new WeakMap();
_lastTime = new WeakMap();
_wheelDelta = new WeakMap();
_capsLock = new WeakMap();
_altKey = new WeakMap();
_moving = new WeakMap();
_rotating = new WeakMap();
_panning = new WeakMap();
_orbiting = new WeakMap();
_disposed = new WeakMap();
_onPointerDown = new WeakMap();
_onPointerMove = new WeakMap();
_onPointerUp = new WeakMap();
_onContextMenu = new WeakMap();
_onWheel = new WeakMap();
_onKeyDown = new WeakMap();
_onKeyUp = new WeakMap();
_onBlur = new WeakMap();
_CameraControl_instances = new WeakSet();
updatePointers_fn = function() {
  const pointers = Array.from(__privateGet(this, _pointers).values());
  __privateSet(this, _rotating, false);
  __privateSet(this, _panning, false);
  __privateSet(this, _orbiting, false);
  if (pointers.length === 0) {
    return false;
  }
  let updated = false;
  if (pointers.length >= 2) {
    const first = pointers[0];
    const second = pointers[1];
    const lastMidX = (first.lastX + second.lastX) * 0.5;
    const lastMidY = (first.lastY + second.lastY) * 0.5;
    const midX = (first.x + second.x) * 0.5;
    const midY = (first.y + second.y) * 0.5;
    const lastDistance = distance(first.lastX, first.lastY, second.lastX, second.lastY);
    const currentDistance = distance(first.x, first.y, second.x, second.y);
    const panX = midX - lastMidX;
    const panY = midY - lastMidY;
    const pinch = currentDistance - lastDistance;
    updated = __privateMethod(this, _CameraControl_instances, panByPixels_fn).call(this, panX, panY) || updated;
    updated = __privateMethod(this, _CameraControl_instances, moveAlongView_fn).call(this, pinch * this.wheelSpeed) || updated;
    __privateSet(this, _panning, Math.abs(panX) + Math.abs(panY) + Math.abs(pinch) > 1e-3);
  } else {
    const pointer = pointers[0];
    const mode = __privateMethod(this, _CameraControl_instances, getPointerMode_fn).call(this, pointer.pointerType, pointer.button);
    if (pointer.mode !== mode) {
      pointer.mode = mode;
      pointer.lastX = pointer.x;
      pointer.lastY = pointer.y;
    }
    const deltaX = pointer.x - pointer.lastX;
    const deltaY = pointer.y - pointer.lastY;
    if (mode === "pan") {
      updated = __privateMethod(this, _CameraControl_instances, panByPixels_fn).call(this, deltaX, deltaY);
      __privateSet(this, _panning, updated);
    } else if (mode === "orbit") {
      updated = __privateMethod(this, _CameraControl_instances, orbitByPixels_fn).call(this, deltaX, deltaY);
      __privateSet(this, _orbiting, true);
    } else {
      updated = __privateMethod(this, _CameraControl_instances, rotateByPixels_fn).call(this, deltaX, deltaY);
      __privateSet(this, _rotating, updated);
    }
  }
  for (const pointer of pointers) {
    pointer.lastX = pointer.x;
    pointer.lastY = pointer.y;
  }
  return updated;
};
updateKeyboard_fn = function(deltaSeconds) {
  const forwardInput = numberFromKey(__privateGet(this, _keys), "KeyW") - numberFromKey(__privateGet(this, _keys), "KeyS");
  const strafeInput = numberFromKey(__privateGet(this, _keys), "KeyD") - numberFromKey(__privateGet(this, _keys), "KeyA");
  const verticalInput = numberFromKey(__privateGet(this, _keys), "KeyQ") - numberFromKey(__privateGet(this, _keys), "KeyE");
  const rollInput = numberFromKey(__privateGet(this, _keys), "KeyR") - numberFromKey(__privateGet(this, _keys), "KeyF");
  const multiplier = __privateMethod(this, _CameraControl_instances, getSpeedMultiplier_fn).call(this);
  let updated = false;
  const movementLength = Math.hypot(forwardInput, strafeInput, verticalInput);
  __privateSet(this, _moving, movementLength > 0);
  if (movementLength > 0) {
    const scale = this.moveSpeed * multiplier * deltaSeconds / Math.max(1, movementLength);
    const basis = getCameraBasis(__privateGet(this, _camera));
    const position = __privateGet(this, _camera).position;
    position.x += (basis.forward.x * forwardInput + basis.right.x * strafeInput + basis.up.x * verticalInput) * scale;
    position.y += (basis.forward.y * forwardInput + basis.right.y * strafeInput + basis.up.y * verticalInput) * scale;
    position.z += (basis.forward.z * forwardInput + basis.right.z * strafeInput + basis.up.z * verticalInput) * scale;
    updated = true;
  }
  if (rollInput !== 0) {
    rollCamera(__privateGet(this, _camera), rollInput * this.rollSpeed * deltaSeconds);
    __privateSet(this, _rotating, true);
    updated = true;
  } else if (__privateGet(this, _pointers).size === 0) {
    __privateSet(this, _rotating, false);
  }
  return updated;
};
updateWheel_fn = function() {
  if (Math.abs(__privateGet(this, _wheelDelta)) < 1e-3) {
    return false;
  }
  const delta = -__privateGet(this, _wheelDelta) * this.wheelSpeed;
  __privateSet(this, _wheelDelta, 0);
  return __privateMethod(this, _CameraControl_instances, moveAlongView_fn).call(this, delta);
};
rotateByPixels_fn = function(deltaX, deltaY) {
  if (Math.abs(deltaX) + Math.abs(deltaY) < 1e-3) {
    return false;
  }
  rotateCamera(__privateGet(this, _camera), -deltaX * this.lookSpeed, -deltaY * this.lookSpeed);
  return true;
};
orbitByPixels_fn = function(deltaX, deltaY) {
  if (Math.abs(deltaX) + Math.abs(deltaY) < 1e-3) {
    return false;
  }
  return orbitCamera(
    __privateGet(this, _camera),
    __privateGet(this, _orbitCenter),
    -deltaX * this.lookSpeed,
    -deltaY * this.lookSpeed,
    this.orbitMinDistance,
    this.orbitMaxDistance,
    this.groundLock
  );
};
panByPixels_fn = function(deltaX, deltaY) {
  if (Math.abs(deltaX) + Math.abs(deltaY) < 1e-3) {
    return false;
  }
  const basis = getCameraBasis(__privateGet(this, _camera));
  const position = __privateGet(this, _camera).position;
  const x = deltaX * this.panSpeed;
  const y = -deltaY * this.panSpeed;
  position.x += basis.right.x * x + basis.viewUp.x * y;
  position.y += basis.right.y * x + basis.viewUp.y * y;
  position.z += basis.right.z * x + basis.viewUp.z * y;
  return true;
};
moveAlongView_fn = function(distanceValue) {
  if (Math.abs(distanceValue) < 1e-3) {
    return false;
  }
  if (this.useOrbit) {
    const center = __privateGet(this, _orbitCenter);
    const camera = __privateGet(this, _camera);
    const offset = subtractVectors(camera.position, center);
    let dist = lengthVector(offset);
    let newDist = dist - distanceValue;
    newDist = clamp(newDist, this.orbitMinDistance, this.orbitMaxDistance || 100);
    const norm = normalizeVector(offset) ?? { x: 0, y: 1, z: 0 };
    camera.position.x = center.x + norm.x * newDist;
    camera.position.y = center.y + norm.y * newDist;
    camera.position.z = center.z + norm.z * newDist;
    return true;
  }
  const forward = getCameraBasis(__privateGet(this, _camera)).forward;
  const position = __privateGet(this, _camera).position;
  position.x += forward.x * distanceValue;
  position.y += forward.y * distanceValue;
  position.z += forward.z * distanceValue;
  return true;
};
getSpeedMultiplier_fn = function() {
  let multiplier = 1;
  if (__privateGet(this, _keys).has("ShiftLeft") || __privateGet(this, _keys).has("ShiftRight")) {
    multiplier *= this.shiftMultiplier;
  }
  if (__privateGet(this, _keys).has("ControlLeft") || __privateGet(this, _keys).has("ControlRight")) {
    multiplier *= this.ctrlMultiplier;
  }
  if (__privateGet(this, _capsLock) || __privateGet(this, _keys).has("CapsLock")) {
    multiplier *= this.capsMultiplier;
  }
  return multiplier;
};
getPointerMode_fn = function(pointerType, button) {
  if (pointerType === "mouse") {
    if (button === 1 || button === 2) {
      return "pan";
    }
    if (button === 0 && this.orbitEnabled && (this.useOrbit || __privateMethod(this, _CameraControl_instances, isOrbitModifierActive_fn).call(this))) {
      return "orbit";
    }
  }
  return "rotate";
};
isOrbitModifierActive_fn = function() {
  return __privateGet(this, _altKey) || __privateGet(this, _keys).has("AltLeft") || __privateGet(this, _keys).has("AltRight");
};
getOrbitDistance_fn = function() {
  return lengthVector(subtractVectors(__privateGet(this, _camera).position, __privateGet(this, _orbitCenter)));
};
function rotateCamera(camera, yawDelta, pitchDelta) {
  const basis = getCameraBasis(camera);
  const orientation = getCameraOrientationBasis(camera);
  const rollAngle = getForwardAxisRoll(orientation.forward, orientation.up, orientation.viewUp);
  const currentPitch = Math.asin(clamp(dotVector(basis.forward, basis.up), -1, 1));
  const nextPitch = clamp(currentPitch + pitchDelta, -MAX_PITCH, MAX_PITCH);
  const horizontalForward = normalizeVector(projectOnPlane(basis.forward, basis.up)) ?? getPerpendicularUnit(basis.up);
  const yawedForward = rotateVectorAroundAxis(horizontalForward, basis.up, yawDelta);
  const forward = normalizeVector(
    addVectors(multiplyVector(yawedForward, Math.cos(nextPitch)), multiplyVector(basis.up, Math.sin(nextPitch)))
  );
  if (!forward) {
    return;
  }
  setCameraLookBasis(camera, forward, getViewUpWithRoll(forward, basis.up, rollAngle));
}
function orbitCamera(camera, center, yawDelta, pitchDelta, minDistance, maxDistance = 100, groundLock = false) {
  const basis = getCameraBasis(camera);
  const orientation = getCameraOrientationBasis(camera);
  const rollAngle = getForwardAxisRoll(orientation.forward, orientation.up, orientation.viewUp);
  const safeMinDistance = Math.max(EPSILON, minDistance);
  let distanceValue = lengthVector(subtractVectors(camera.position, center));
  let forward = normalizeVector(subtractVectors(center, camera.position)) ?? normalizeVector(orientation.forward) ?? { x: 0, y: 0, z: -1 };
  if (distanceValue < safeMinDistance) {
    distanceValue = safeMinDistance;
    forward = normalizeVector(orientation.forward) ?? forward;
  } else if (distanceValue > maxDistance) {
    distanceValue = maxDistance;
  }
  const currentPitch = Math.asin(clamp(dotVector(forward, basis.up), -1, 1));
  const maxPitchLimit = groundLock ? 0 : MAX_PITCH;
  const nextPitch = clamp(currentPitch + pitchDelta, -MAX_PITCH, maxPitchLimit);
  const horizontalForward = normalizeVector(projectOnPlane(forward, basis.up)) ?? getPerpendicularUnit(basis.up);
  const yawedForward = rotateVectorAroundAxis(horizontalForward, basis.up, yawDelta);
  const nextForward = normalizeVector(
    addVectors(multiplyVector(yawedForward, Math.cos(nextPitch)), multiplyVector(basis.up, Math.sin(nextPitch)))
  );
  if (!nextForward) {
    return false;
  }
  camera.position.x = center.x - nextForward.x * distanceValue;
  camera.position.y = center.y - nextForward.y * distanceValue;
  camera.position.z = center.z - nextForward.z * distanceValue;
  setCameraLookBasis(camera, nextForward, getViewUpWithRoll(nextForward, basis.up, rollAngle));
  return true;
}
function rollCamera(camera, rollDelta) {
  const basis = getCameraOrientationBasis(camera);
  const viewUp = normalizeVector(rotateVectorAroundAxis(basis.viewUp, basis.forward, -rollDelta));
  if (!viewUp) {
    return;
  }
  setCameraLookBasis(camera, basis.forward, viewUp);
}
function getCameraBasis(camera) {
  const orientation = getCameraOrientationBasis(camera);
  const right = normalizeVector(crossVectors(orientation.forward, orientation.up)) ?? orientation.right;
  const viewUp = normalizeVector(crossVectors(right, orientation.forward)) ?? orientation.viewUp;
  return {
    forward: orientation.forward,
    right,
    up: orientation.up,
    viewUp
  };
}
function getCameraOrientationBasis(camera) {
  const up = getCameraUp(camera);
  const matrix = getCameraRotationMatrix(camera);
  const elements = matrix._elements;
  const forward = normalizeVector({
    x: -elements[8],
    y: -elements[9],
    z: -elements[10]
  }) ?? { x: 0, y: 0, z: -1 };
  const matrixRight = normalizeVector({
    x: elements[0],
    y: elements[1],
    z: elements[2]
  }) ?? getPerpendicularUnit(up);
  const viewUp = normalizeVector({
    x: elements[4],
    y: elements[5],
    z: elements[6]
  }) ?? normalizeVector(crossVectors(matrixRight, forward)) ?? up;
  return {
    forward,
    right: matrixRight,
    up,
    viewUp
  };
}
function getForwardAxisRoll(forward, up, viewUp) {
  const levelViewUp = getViewUpWithRoll(forward, up, 0);
  return angleAroundAxis(levelViewUp, viewUp, forward);
}
function getViewUpWithRoll(forward, up, rollAngle) {
  const right = normalizeVector(crossVectors(forward, up)) ?? getPerpendicularUnit(forward);
  const viewUp = normalizeVector(crossVectors(right, forward)) ?? up;
  return normalizeVector(rotateVectorAroundAxis(viewUp, forward, rollAngle)) ?? viewUp;
}
function setCameraLookBasis(camera, forward, up) {
  const right = normalizeVector(crossVectors(forward, up)) ?? getPerpendicularUnit(up);
  const viewUp = normalizeVector(crossVectors(right, forward)) ?? up;
  const back = multiplyVector(forward, -1);
  const matrix = makeBasisMatrix(right, viewUp, back);
  const rotation = camera.rotation;
  const matrixRotation = rotation;
  if (typeof matrixRotation.setFromRotationMatrix === "function") {
    matrixRotation.setFromRotationMatrix(matrix, rotation.order);
    return;
  }
  const euler = getEulerFromRotationMatrix(matrix, rotation.order ?? "XYZ");
  if (typeof rotation.set === "function") {
    rotation.set(euler.x, euler.y, euler.z, euler.order);
  } else {
    rotation.x = euler.x;
    rotation.y = euler.y;
    rotation.z = euler.z;
  }
}
function getCameraUp(camera) {
  return normalizeVector(camera.up ?? DEFAULT_UP) ?? DEFAULT_UP;
}
function getCameraRotationMatrix(camera) {
  if (camera.quaternion) {
    return makeRotationMatrixFromQuaternion(camera.quaternion);
  }
  return makeRotationMatrixFromEuler(camera.rotation);
}
function makeRotationMatrixFromQuaternion(quaternion) {
  const { x, y, z, w } = quaternion;
  const x2 = x + x;
  const y2 = y + y;
  const z2 = z + z;
  const xx = x * x2;
  const xy = x * y2;
  const xz = x * z2;
  const yy = y * y2;
  const yz = y * z2;
  const zz = z * z2;
  const wx = w * x2;
  const wy = w * y2;
  const wz = w * z2;
  return makeMatrix([
    1 - (yy + zz),
    xy + wz,
    xz - wy,
    0,
    xy - wz,
    1 - (xx + zz),
    yz + wx,
    0,
    xz + wy,
    yz - wx,
    1 - (xx + yy),
    0,
    0,
    0,
    0,
    1
  ]);
}
function makeRotationMatrixFromEuler(rotation) {
  const x = rotation.x;
  const y = rotation.y;
  const z = rotation.z;
  const a = Math.cos(x);
  const b = Math.sin(x);
  const c = Math.cos(y);
  const d = Math.sin(y);
  const e = Math.cos(z);
  const f = Math.sin(z);
  const ae = a * e;
  const af = a * f;
  const be = b * e;
  const bf = b * f;
  return makeMatrix([
    c * e,
    af + be * d,
    bf - ae * d,
    0,
    -c * f,
    ae - bf * d,
    be + af * d,
    0,
    d,
    -b * c,
    a * c,
    0,
    0,
    0,
    0,
    1
  ]);
}
function makeBasisMatrix(xAxis, yAxis, zAxis) {
  return makeMatrix([
    xAxis.x,
    xAxis.y,
    xAxis.z,
    0,
    yAxis.x,
    yAxis.y,
    yAxis.z,
    0,
    zAxis.x,
    zAxis.y,
    zAxis.z,
    0,
    0,
    0,
    0,
    1
  ]);
}
function makeMatrix(elements) {
  return {
    _elements: Float32Array.from(elements)
  };
}
function getEulerFromRotationMatrix(matrix, order) {
  const te = matrix._elements;
  const m11 = te[0];
  const m12 = te[4];
  const m13 = te[8];
  const m23 = te[9];
  const m33 = te[10];
  const euler = {
    x: 0,
    y: Math.asin(clamp(m13, -1, 1)),
    z: 0,
    order
  };
  if (Math.abs(m13) < 0.99999) {
    euler.x = Math.atan2(-m23, m33);
    euler.z = Math.atan2(-m12, m11);
  } else {
    const m22 = te[5];
    const m32 = te[6];
    euler.x = Math.atan2(m32, m22);
  }
  return euler;
}
function projectOnPlane(vector, normal) {
  return subtractVectors(vector, multiplyVector(normal, dotVector(vector, normal)));
}
function angleAroundAxis(from, to, axis) {
  const projectedFrom = normalizeVector(projectOnPlane(from, axis));
  const projectedTo = normalizeVector(projectOnPlane(to, axis));
  if (!projectedFrom || !projectedTo) {
    return 0;
  }
  return Math.atan2(dotVector(crossVectors(projectedFrom, projectedTo), axis), dotVector(projectedFrom, projectedTo));
}
function rotateVectorAroundAxis(vector, axis, angle) {
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  const cross = crossVectors(axis, vector);
  const axisScale = dotVector(axis, vector) * (1 - cos);
  return addVectors(
    addVectors(multiplyVector(vector, cos), multiplyVector(cross, sin)),
    multiplyVector(axis, axisScale)
  );
}
function getPerpendicularUnit(axis) {
  const helper = Math.abs(axis.y) < 0.9 ? { x: 0, y: 1, z: 0 } : { x: 1, y: 0, z: 0 };
  return normalizeVector(crossVectors(axis, helper)) ?? { x: 1, y: 0, z: 0 };
}
function addVectors(a, b) {
  return {
    x: a.x + b.x,
    y: a.y + b.y,
    z: a.z + b.z
  };
}
function subtractVectors(a, b) {
  return {
    x: a.x - b.x,
    y: a.y - b.y,
    z: a.z - b.z
  };
}
function multiplyVector(vector, scale) {
  return {
    x: vector.x * scale,
    y: vector.y * scale,
    z: vector.z * scale
  };
}
function copyVector(vector) {
  return {
    x: vector.x,
    y: vector.y,
    z: vector.z
  };
}
function lengthVector(vector) {
  return Math.hypot(vector.x, vector.y, vector.z);
}
function dotVector(a, b) {
  return a.x * b.x + a.y * b.y + a.z * b.z;
}
function crossVectors(a, b) {
  return {
    x: a.y * b.z - a.z * b.y,
    y: a.z * b.x - a.x * b.z,
    z: a.x * b.y - a.y * b.x
  };
}
function normalizeVector(vector) {
  const length = Math.hypot(vector.x, vector.y, vector.z);
  if (length < EPSILON) {
    return void 0;
  }
  return {
    x: vector.x / length,
    y: vector.y / length,
    z: vector.z / length
  };
}
function numberFromKey(keys, code) {
  return keys.has(code) ? 1 : 0;
}
function distance(x1, y1, x2, y2) {
  return Math.hypot(x2 - x1, y2 - y1);
}
function clamp(value, minimum, maximum) {
  return Math.min(Math.max(value, minimum), maximum);
}
export {
  CameraControl
};
