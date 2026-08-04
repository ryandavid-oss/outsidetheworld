(function attachSuperFrgmntsBeam(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  root.SuperFrgmntsBeam = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function makeBeamAPI() {
  "use strict";

  const MODULES = Object.freeze({
    FOCUS: "focusPulse",
    RIME: "rimeLock",
    GHOST: "ghostVector",
    PRISM: "prismSplinter",
    SOLAR: "solarNeedle",
  });

  const DISPLAY_ORDER = Object.freeze([
    MODULES.FOCUS,
    MODULES.RIME,
    MODULES.GHOST,
    MODULES.PRISM,
    MODULES.SOLAR,
  ]);

  const MODULE_INFO = Object.freeze({
    [MODULES.FOCUS]: Object.freeze({
      name: "Focus Pulse",
      code: "FOC",
      color: "#ffa81a",
      capability: "Hold Fire to charge damage and size.",
      compromise: "Charging suppresses automatic fire.",
    }),
    [MODULES.RIME]: Object.freeze({
      name: "Rime Lock",
      code: "RIM",
      color: "#40e0ff",
      capability: "Freezes ordinary enemies for 2.8 seconds.",
      compromise: "Moderate direct damage; bosses resist freezing.",
    }),
    [MODULES.GHOST]: Object.freeze({
      name: "Ghost Vector",
      code: "GHO",
      color: "#e038ff",
      capability: "Faster shots pass through terrain and closed doors.",
      compromise: "Removes mid-flight guidance.",
    }),
    [MODULES.PRISM]: Object.freeze({
      name: "Prism Splinter",
      code: "PRI",
      color: "#6bff29",
      capability: "Opens to three Aryn-height lanes, then flies straight.",
      compromise: "Removes guidance; damage must be aligned.",
    }),
    [MODULES.SOLAR]: Object.freeze({
      name: "Solar Needle",
      code: "SOL",
      color: "#ff3d12",
      capability: "High direct damage and enemy penetration.",
      compromise: "Guidance is substantially reduced.",
    }),
  });

  const CONSTANTS = Object.freeze({
    baseCooldown: 0.18,
    baseSpeed: 560,
    lifetime: 0.9,
    seekerRange: 420,
    seekerResponse: 1.65,
    focusChargeDuration: 1.15,
    clearanceDistance: 38,
    trailPoints: 11,
  });

  const PALETTE = Object.freeze({
    neutral: Object.freeze({ body: "#59f5de", glow: "#42d8c8", trail: "#3ecfbe" }),
    [MODULES.FOCUS]: Object.freeze({ body: "#ffa81a", glow: "#ffb62e", trail: "#e89b18" }),
    [MODULES.RIME]: Object.freeze({ body: "#40e0ff", glow: "#5ceaff", trail: "#43cce8" }),
    [MODULES.GHOST]: Object.freeze({ body: "#e038ff", glow: "#ef55ff", trail: "#b92fd7" }),
    [MODULES.PRISM]: Object.freeze({ body: "#6bff29", glow: "#7dff42", trail: "#54d821" }),
    [MODULES.SOLAR]: Object.freeze({ body: "#ff3d12", glow: "#ff5a1f", trail: "#e23810" }),
  });

  function clamp(value, minimum, maximum) {
    return Math.min(maximum, Math.max(minimum, value));
  }

  function normalizeModules(modules) {
    const source = modules instanceof Set ? Array.from(modules) : (modules || []);
    return new Set(source.filter((module) => DISPLAY_ORDER.includes(module)));
  }

  function resolveRecipe(enabledModules, rawChargeFraction) {
    const modules = normalizeModules(enabledModules);
    const hasFocus = modules.has(MODULES.FOCUS);
    const hasRime = modules.has(MODULES.RIME);
    const hasGhost = modules.has(MODULES.GHOST);
    const hasPrism = modules.has(MODULES.PRISM);
    const hasSolar = modules.has(MODULES.SOLAR);
    const chargeFraction = hasFocus ? clamp(Number(rawChargeFraction) || 0, 0, 1) : 0;
    const thermalShock = hasRime && hasSolar;

    let damagePerProjectile = hasSolar ? 2 : 1;
    if (thermalShock) damagePerProjectile += 1;
    if (hasFocus) {
      if (chargeFraction >= 0.82) damagePerProjectile += 2;
      else if (chargeFraction >= 0.34) damagePerProjectile += 1;
    }

    const laneOffsets = hasPrism ? [-7, 0, 7] : [0];
    const laneTerminalOffsets = hasPrism ? [-56, 0, 56] : [0];
    const laneSpreadDistance = hasPrism ? 132 : 0;
    if (hasPrism && hasSolar) {
      damagePerProjectile = Math.max(1, damagePerProjectile - 1);
    }

    let guidanceMultiplier = 1;
    if (hasGhost || hasPrism) guidanceMultiplier = 0;
    else if (hasSolar) guidanceMultiplier = 0.35;

    let cooldownMultiplier = 1;
    if (chargeFraction >= 0.34) cooldownMultiplier += 0.12 + chargeFraction * 0.1;
    if (modules.size >= 4) cooldownMultiplier += 0.08;

    return {
      modules,
      chargeFraction,
      laneOffsets,
      laneTerminalOffsets,
      laneSpreadDistance,
      damagePerProjectile,
      speedMultiplier: hasGhost ? 1.22 : 1,
      sizeMultiplier: 1 + (hasFocus ? chargeFraction * 1.2 : 0) + (hasSolar ? 0.12 : 0),
      guidanceMultiplier,
      cooldownMultiplier,
      phasesThroughTerrain: hasGhost,
      penetratesEnemies: hasSolar,
      freezeDuration: hasRime && !hasSolar ? 2.8 : 0,
      causesThermalShock: thermalShock,
      clearanceDistance: CONSTANTS.clearanceDistance,
    };
  }

  function initialVelocity(origin, target, direction, speed, canAim) {
    if (!target || !canAim) return { x: speed * direction, y: 0 };
    const dx = target.x - origin.x;
    const dy = target.y - origin.y;
    if (dx * direction <= 0) return { x: speed * direction, y: 0 };
    const distance = Math.max(1, Math.hypot(dx, dy));
    return { x: (dx / distance) * speed, y: (dy / distance) * speed };
  }

  function createVolley(options) {
    const opts = options || {};
    const recipe = resolveRecipe(opts.enabledModules, opts.chargeFraction);
    const direction = opts.direction === -1 ? -1 : 1;
    const speed = CONSTANTS.baseSpeed * recipe.speedMultiplier;
    const originX = Number(opts.x) || 0;
    const originY = Number(opts.y) || 0;
    const baseID = Number(opts.idBase) || 0;
    const canAim = !recipe.modules.has(MODULES.PRISM);

    return recipe.laneOffsets.map((laneOffset, laneIndex) => {
      const origin = { x: originX, y: originY + laneOffset };
      const velocity = initialVelocity(origin, opts.target, direction, speed, canAim);
      return {
        id: baseID + laneIndex + 1,
        x: origin.x,
        y: origin.y,
        velocityX: velocity.x,
        velocityY: velocity.y,
        direction,
        lifetime: CONSTANTS.lifetime,
        age: 0,
        trail: [],
        recipe,
        targetID: opts.target ? opts.target.id || null : null,
        prismLane: recipe.laneOffsets.length === 3 ? laneIndex - 1 : 0,
        prismInitialOffset: laneOffset,
        prismTerminalOffset: recipe.laneTerminalOffsets[laneIndex],
        prismSpreadDistance: recipe.laneSpreadDistance,
        distanceTravelled: 0,
        hitEnemyIDs: new Set(),
      };
    });
  }

  function prismLaneOffset(projectile, distance) {
    if (projectile.prismLane === 0 || projectile.prismSpreadDistance <= 0) {
      return projectile.prismInitialOffset;
    }
    const progress = clamp(distance / projectile.prismSpreadDistance, 0, 1);
    const inverse = 1 - progress;
    const easedProgress = 1 - inverse * inverse * inverse;
    return projectile.prismInitialOffset +
      (projectile.prismTerminalOffset - projectile.prismInitialOffset) * easedProgress;
  }

  function updateGuidance(projectile, deltaSeconds, target) {
    if (!target || projectile.recipe.guidanceMultiplier <= 0) return;
    const dx = target.x - projectile.x;
    const dy = target.y - projectile.y;
    const distance = Math.max(1, Math.hypot(dx, dy));
    if (distance > CONSTANTS.seekerRange) return;
    const speed = Math.max(1, Math.hypot(projectile.velocityX, projectile.velocityY));
    const desiredX = (dx / distance) * speed;
    const desiredY = (dy / distance) * speed;
    const response = Math.min(
      1,
      CONSTANTS.seekerResponse * projectile.recipe.guidanceMultiplier * deltaSeconds,
    );
    projectile.velocityX += (desiredX - projectile.velocityX) * response;
    projectile.velocityY += (desiredY - projectile.velocityY) * response;
    const correctedSpeed = Math.max(1, Math.hypot(projectile.velocityX, projectile.velocityY));
    projectile.velocityX = (projectile.velocityX / correctedSpeed) * speed;
    projectile.velocityY = (projectile.velocityY / correctedSpeed) * speed;
  }

  function appendReusableTrailPoint(trail, x, y, limit) {
    if (trail.length < limit) {
      trail.push({ x, y });
      return;
    }
    const oldestPoint = trail.shift();
    oldestPoint.x = x;
    oldestPoint.y = y;
    trail.push(oldestPoint);
  }

  function updateProjectile(projectile, deltaSeconds, target) {
    const dt = clamp(Number(deltaSeconds) || 0, 0, 1 / 15);
    projectile.age += dt;
    projectile.lifetime -= dt;
    appendReusableTrailPoint(
      projectile.trail,
      projectile.x,
      projectile.y,
      CONSTANTS.trailPoints,
    );

    updateGuidance(projectile, dt, target);
    const previousDistance = projectile.distanceTravelled;
    const deltaX = projectile.velocityX * dt;
    const deltaY = projectile.velocityY * dt;
    const nextDistance = previousDistance + Math.hypot(deltaX, deltaY);
    projectile.x += deltaX;
    projectile.y += deltaY;
    if (projectile.prismLane !== 0) {
      projectile.y += prismLaneOffset(projectile, nextDistance) -
        prismLaneOffset(projectile, previousDistance);
    }
    projectile.distanceTravelled = nextDistance;
    return projectile;
  }

  function clearanceFraction(projectile) {
    if (projectile.recipe.clearanceDistance <= 0) return 1;
    return clamp(projectile.distanceTravelled / projectile.recipe.clearanceDistance, 0, 1);
  }

  function projectileBounds(projectile) {
    const width = 24 * projectile.recipe.sizeMultiplier;
    const height = 6 * projectile.recipe.sizeMultiplier;
    return { x: projectile.x - width / 2, y: projectile.y - height / 2, width, height };
  }

  function applyHit(enemy, projectile) {
    const previousHealth = Math.max(0, Number(enemy.health) || 0);
    const inflictedDamage = Math.min(previousHealth, projectile.recipe.damagePerProjectile);
    enemy.health = Math.max(0, previousHealth - projectile.recipe.damagePerProjectile);
    if (projectile.recipe.causesThermalShock) {
      enemy.freezeRemaining = 0;
    } else if (
      projectile.recipe.freezeDuration > 0 &&
      !enemy.isBoss &&
      enemy.health > 0
    ) {
      enemy.freezeRemaining = Math.max(
        Number(enemy.freezeRemaining) || 0,
        projectile.recipe.freezeDuration,
      );
      enemy.velocityX = 0;
      enemy.velocityY = 0;
    }
    projectile.hitEnemyIDs.add(enemy.id);
    return {
      damage: inflictedDamage,
      remainingHealth: enemy.health,
      frozen: (enemy.freezeRemaining || 0) > 0,
      thermalShock: projectile.recipe.causesThermalShock,
      projectileSurvives: projectile.recipe.penetratesEnemies,
    };
  }

  function paletteFor(projectile) {
    const modules = projectile.recipe.modules;
    if (modules.has(MODULES.SOLAR)) return PALETTE[MODULES.SOLAR];
    if (modules.has(MODULES.PRISM)) return PALETTE[MODULES.PRISM];
    if (modules.has(MODULES.GHOST)) return PALETTE[MODULES.GHOST];
    if (modules.has(MODULES.RIME)) return PALETTE[MODULES.RIME];
    if (modules.has(MODULES.FOCUS)) return PALETTE[MODULES.FOCUS];
    return PALETTE.neutral;
  }

  function dimensionsFor(projectile) {
    const charge = projectile.recipe.chargeFraction;
    const modules = projectile.recipe.modules;
    const width = 28 + (modules.has(MODULES.SOLAR) ? 14 : 0) +
      (modules.has(MODULES.PRISM) ? 8 : 0) + charge * 13;
    const height = 5 + charge * 11 + (modules.has(MODULES.SOLAR) ? 1 : 0);
    return {
      glowWidth: width + 8,
      glowHeight: height + 6,
      bodyWidth: width,
      bodyHeight: height,
      coreWidth: Math.max(12, width - 7),
      coreHeight: Math.max(2, Math.min(4, height * 0.34)),
    };
  }

  function trailStyleFor(projectile) {
    const modules = projectile.recipe.modules;
    if (modules.has(MODULES.SOLAR)) return { width: 3.2, blur: 7, alpha: 0.82 };
    if (modules.has(MODULES.PRISM)) return { width: 1.9, blur: 4, alpha: 0.76 };
    if (modules.has(MODULES.GHOST)) return { width: 1.5, blur: 4, alpha: 0.68 };
    if (modules.has(MODULES.RIME)) return { width: 2.2, blur: 5, alpha: 0.74 };
    if (modules.has(MODULES.FOCUS)) return { width: 3.4, blur: 7, alpha: 0.8 };
    return { width: 2.6, blur: 6, alpha: 0.74 };
  }

  function roundedRectPath(ctx, x, y, width, height, radius) {
    const r = Math.min(Math.abs(width) / 2, Math.abs(height) / 2, radius);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + width - r, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + r);
    ctx.lineTo(x + width, y + height - r);
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    ctx.lineTo(x + r, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  function usesSoftShadows(options) {
    return !options || options.softShadows !== false;
  }

  function setBeamShadow(ctx, blur, options) {
    ctx.shadowBlur = usesSoftShadows(options) ? blur : 0;
  }

  function drawTrail(ctx, projectile, palette, style, options) {
    if (projectile.trail.length < 2) return;
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    ctx.strokeStyle = palette.trail;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.shadowColor = palette.glow;
    setBeamShadow(ctx, style.blur, options);
    ctx.beginPath();
    projectile.trail.forEach((point, index) => {
      if (index === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.lineTo(projectile.x, projectile.y);
    ctx.globalAlpha = style.alpha;
    ctx.strokeStyle = palette.trail;
    ctx.lineWidth = style.width;
    ctx.stroke();
    ctx.restore();
  }

  function drawCoreBody(ctx, projectile, dimensions, palette, options) {
    const modules = projectile.recipe.modules;
    const hasFocusBody = modules.has(MODULES.FOCUS) &&
      projectile.recipe.chargeFraction >= 0.18 &&
      !modules.has(MODULES.SOLAR);

    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    ctx.fillStyle = palette.glow;
    ctx.globalAlpha = modules.has(MODULES.GHOST) ? 0.3 : 0.48;
    ctx.shadowColor = palette.glow;
    setBeamShadow(ctx, modules.has(MODULES.GHOST) ? 3 : 7, options);
    roundedRectPath(
      ctx,
      -dimensions.glowWidth / 2,
      -dimensions.glowHeight / 2,
      dimensions.glowWidth,
      dimensions.glowHeight,
      dimensions.glowHeight / 2,
    );
    ctx.fill();

    ctx.globalAlpha = modules.has(MODULES.GHOST) ? 0.62 : 0.92;
    ctx.fillStyle = palette.body;
    ctx.strokeStyle = palette.body;
    ctx.lineWidth = modules.has(MODULES.GHOST) ? 0.65 : 0.9;
    setBeamShadow(
      ctx,
      modules.has(MODULES.GHOST) ? 1.2 : modules.has(MODULES.PRISM) ? 1.5 : 2.5,
      options,
    );
    if (hasFocusBody) {
      ctx.beginPath();
      ctx.ellipse(0, 0, dimensions.bodyWidth / 2, dimensions.bodyHeight / 2, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    } else if (modules.has(MODULES.PRISM)) {
      const halfWidth = dimensions.bodyWidth / 2;
      const halfHeight = dimensions.bodyHeight / 2;
      ctx.beginPath();
      ctx.moveTo(-halfWidth, 0);
      ctx.lineTo(halfWidth * 0.62, halfHeight);
      ctx.lineTo(halfWidth, 0);
      ctx.lineTo(halfWidth * 0.62, -halfHeight);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else {
      roundedRectPath(
        ctx,
        -dimensions.bodyWidth / 2,
        -dimensions.bodyHeight / 2,
        dimensions.bodyWidth,
        dimensions.bodyHeight,
        dimensions.bodyHeight / 2,
      );
      ctx.fill();
      ctx.stroke();
    }

    ctx.globalAlpha = modules.has(MODULES.GHOST) ? 0.7 : 0.92;
    ctx.fillStyle = "#ffffff";
    ctx.shadowColor = "#ffffff";
    setBeamShadow(ctx, 3, options);
    roundedRectPath(
      ctx,
      -dimensions.coreWidth / 2,
      -dimensions.coreHeight / 2,
      dimensions.coreWidth,
      dimensions.coreHeight,
      dimensions.coreHeight / 2,
    );
    ctx.fill();
    ctx.restore();
  }

  function drawGhost(ctx, projectile, options) {
    const phaseShift = projectile.age * 18;
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    ctx.strokeStyle = "rgba(235,77,255,0.88)";
    ctx.lineWidth = 1.15;
    ctx.shadowColor = "#e038ff";
    setBeamShadow(ctx, 3.6, options);
    [0, Math.PI].forEach((phase) => {
      ctx.beginPath();
      for (let step = 0; step <= 16; step += 1) {
        const x = -22 + (step / 16) * 44;
        const y = Math.sin((step / 16) * Math.PI * 3 + phase + phaseShift) * 5;
        if (step === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    });
    ctx.restore();
  }

  function drawRime(ctx, projectile, options) {
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    ctx.beginPath();
    ctx.moveTo(-13, 0);
    ctx.lineTo(0, 5.5);
    ctx.lineTo(13, 0);
    ctx.lineTo(0, -5.5);
    ctx.closePath();
    ctx.fillStyle = "rgba(122,240,255,0.54)";
    ctx.strokeStyle = "rgba(224,255,255,0.94)";
    ctx.lineWidth = 0.8;
    ctx.shadowColor = "#77edff";
    setBeamShadow(ctx, 6, options);
    ctx.fill();
    ctx.stroke();

    for (let index = 0; index < 3; index += 1) {
      const cycle = (projectile.age / 0.22 + index * 0.3) % 1;
      const x = -15 + index * 10 - cycle * 3;
      const baseY = index % 2 === 0 ? 7 : -7;
      const y = baseY + cycle * (baseY > 0 ? 5 : -5);
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(Math.PI / 4);
      ctx.globalAlpha = 1 - cycle * 0.82;
      ctx.fillStyle = "#b8fbff";
      ctx.fillRect(-1.5, -1.5, 3, 3);
      ctx.restore();
    }
    ctx.restore();
  }

  function drawFocus(ctx, projectile, options) {
    if (projectile.recipe.chargeFraction < 0.18) return;
    const pulse = (projectile.age / 0.16) % 1;
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    [0, 1].forEach((index) => {
      const resetScale = 1 - pulse * 0.2;
      ctx.save();
      ctx.scale(resetScale, resetScale);
      ctx.globalAlpha = (index === 0 ? 0.62 : 0.34) * (1 - pulse * 0.55);
      ctx.strokeStyle = "#ffb82e";
      ctx.lineWidth = index === 0 ? 1.1 : 0.7;
      ctx.shadowColor = "#ffa81a";
      setBeamShadow(ctx, 6, options);
      ctx.beginPath();
      ctx.ellipse(0, 0, (29 + index * 8) / 2, (20 + index * 6) / 2, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    });

    const radius = 10 + projectile.recipe.chargeFraction * 6;
    const rotation = projectile.age / 0.46 * Math.PI * 2;
    for (let index = 0; index < 3; index += 1) {
      const angle = (index / 3) * Math.PI * 2 + rotation;
      ctx.beginPath();
      ctx.fillStyle = "#ffffff";
      ctx.shadowColor = "#ffb82e";
      setBeamShadow(ctx, 8, options);
      ctx.arc(Math.cos(angle) * radius, Math.sin(angle) * radius, 1.4, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawPrism(ctx, projectile, dimensions, options) {
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    const halfWidth = dimensions.bodyWidth / 2;
    ctx.beginPath();
    ctx.moveTo(-halfWidth * 0.72, 0);
    ctx.lineTo(halfWidth * 0.56, 0);
    ctx.lineTo(halfWidth * 0.78, 1.25);
    ctx.strokeStyle = "rgba(230,255,189,0.96)";
    ctx.lineWidth = 0.9;
    ctx.shadowColor = "#9cff61";
    setBeamShadow(ctx, 4, options);
    ctx.stroke();
    ctx.restore();
  }

  function drawSolar(ctx, projectile, options) {
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    const heatScale = 0.78 + ((Math.sin(projectile.age * 39) + 1) / 2) * 0.57;
    ctx.globalAlpha = 0.2;
    ctx.fillStyle = "#ff3108";
    ctx.strokeStyle = "#ff8014";
    ctx.shadowColor = "#ff3d12";
    setBeamShadow(ctx, 12, options);
    ctx.beginPath();
    ctx.ellipse(0, 0, 28, 7 * heatScale, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.globalAlpha = 1;
    ctx.beginPath();
    ctx.moveTo(27, 0);
    ctx.lineTo(18, 3.1);
    ctx.lineTo(18, -3.1);
    ctx.closePath();
    ctx.fillStyle = "#ffffff";
    ctx.strokeStyle = "rgba(255,148,36,0.88)";
    ctx.lineWidth = 0.7;
    ctx.shadowColor = "#ff8b21";
    setBeamShadow(ctx, 3, options);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  function stableNoise(seed) {
    const value = Math.sin(seed * 12.9898) * 43758.5453;
    return value - Math.floor(value);
  }

  function drawParticles(ctx, projectile, dimensions, palette, options) {
    const modules = projectile.recipe.modules;
    if (!modules.has(MODULES.SOLAR) && !modules.has(MODULES.PRISM) && !modules.has(MODULES.RIME)) {
      return;
    }
    const count = modules.has(MODULES.SOLAR) ? 5 : modules.has(MODULES.RIME) ? 4 : 3;
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    ctx.fillStyle = modules.has(MODULES.RIME) ? "#9ef6ff" : palette.body;
    ctx.shadowColor = palette.glow;
    setBeamShadow(ctx, 4, options);
    for (let index = 0; index < count; index += 1) {
      const cycle = (projectile.age * (4.5 + index * 0.2) + index / count) % 1;
      const spread = modules.has(MODULES.RIME) ? 8 : 4;
      const x = -dimensions.bodyWidth / 2 - cycle * (10 + index * 2);
      const y = (stableNoise(projectile.id * 7 + index * 13) - 0.5) * spread +
        Math.sin(projectile.age * 17 + index) * 1.2;
      ctx.globalAlpha = 0.75 * (1 - cycle);
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(Math.PI / 4 + index * 0.3);
      const size = modules.has(MODULES.SOLAR) ? 1.4 : 1.1;
      ctx.fillRect(-size / 2, -size / 2, size, size);
      ctx.restore();
    }
    ctx.restore();
  }

  function drawProjectile(ctx, projectile, options) {
    const opts = options || {};
    const palette = paletteFor(projectile);
    const trailStyle = trailStyleFor(projectile);
    const dimensions = dimensionsFor(projectile);
    drawTrail(ctx, projectile, palette, trailStyle, opts);

    const rotation = Math.atan2(projectile.velocityY, projectile.velocityX);
    const clearance = clearanceFraction(projectile);
    const bloomX = 0.46 + clearance * 0.54;
    const bloomY = 0.38 + clearance * 0.62;
    const alpha = 0.64 + clearance * 0.36;
    const visualScale = Number(opts.visualScale) || 1;

    ctx.save();
    ctx.translate(projectile.x, projectile.y);
    ctx.rotate(rotation);
    if (projectile.direction < 0 && Math.abs(rotation) > Math.PI / 2) {
      // Geometry already follows rotation; preserve upright asymmetrical layers.
    }
    ctx.scale(bloomX * visualScale, bloomY * visualScale);
    ctx.globalAlpha = alpha;
    drawCoreBody(ctx, projectile, dimensions, palette, opts);
    if (projectile.recipe.modules.has(MODULES.GHOST)) drawGhost(ctx, projectile, opts);
    if (projectile.recipe.modules.has(MODULES.RIME)) drawRime(ctx, projectile, opts);
    if (projectile.recipe.modules.has(MODULES.FOCUS)) drawFocus(ctx, projectile, opts);
    if (projectile.recipe.modules.has(MODULES.PRISM)) drawPrism(ctx, projectile, dimensions, opts);
    if (projectile.recipe.modules.has(MODULES.SOLAR)) drawSolar(ctx, projectile, opts);
    drawParticles(ctx, projectile, dimensions, palette, opts);
    ctx.restore();
  }

  return Object.freeze({
    MODULES,
    DISPLAY_ORDER,
    MODULE_INFO,
    CONSTANTS,
    resolveRecipe,
    createVolley,
    updateProjectile,
    clearanceFraction,
    projectileBounds,
    prismLaneOffset,
    applyHit,
    drawProjectile,
  });
});
