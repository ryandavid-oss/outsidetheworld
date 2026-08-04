(function attachPageDestructionEncounter() {
    "use strict";

    var trigger = document.getElementById("destroyPageButton");
    var overlay = document.getElementById("pageDestruction");
    var facade = document.getElementById("pageDestructionFacade");
    var canvas = document.getElementById("pageDestructionCanvas");
    var statusText = document.getElementById("pageDestructionStatus");
    var meterText = document.getElementById("pageDestructionMeter");
    var restoreButton = document.getElementById("restoreTimelineButton");
    var pageMain = document.querySelector("main");
    if (!trigger || !overlay || !facade || !canvas || !statusText || !meterText || !restoreButton) return;

    var context = canvas.getContext("2d");
    var Beam = window.SuperFrgmntsBeam;
    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var animationFrame = 0;
    var firingTimer = 0;
    var shakeTimer = 0;
    var startTimer = 0;
    var preparing = false;
    var pendingScrollY = 0;
    var encounter = null;
    var deviceScale = 1;

    var shotTimes = [1.6, 3.0, 4.4, 5.8, 7.2, 8.6, 10.0, 11.4, 12.8, 14.2, 15.6, 17.0, 18.4, 21.2];
    var killShotIndex = 13;
    var runnerJumpTimes = [4.05, 8.05, 12.35, 16.35];
    var enemyRoute = [
        { time: 0, x: 0.62 },
        { time: 2.7, x: 0.86 },
        { time: 3.35, x: 0.82 },
        { time: 6.1, x: 0.16 },
        { time: 6.85, x: 0.22 },
        { time: 10.2, x: 0.88 },
        { time: 10.95, x: 0.82 },
        { time: 14.3, x: 0.12 },
        { time: 15.05, x: 0.2 },
        { time: 18.3, x: 0.86 },
        { time: 19.2, x: 0.72 },
        { time: 21.0, x: 0.64 },
        { time: 24.8, x: 0.64 }
    ];
    var enemyLeapWindows = [
        { start: 3.75, end: 5.25, height: 0.18 },
        { start: 7.7, end: 9.25, height: 0.22 },
        { start: 12.0, end: 13.55, height: 0.18 },
        { start: 16.0, end: 17.6, height: 0.22 }
    ];
    var shardClips = [
        "polygon(0 0, 33.34% 0, 0 50%)",
        "polygon(33.34% 0, 33.34% 50%, 0 50%)",
        "polygon(33.33% 0, 66.67% 0, 33.33% 50%)",
        "polygon(66.67% 0, 66.67% 50%, 33.33% 50%)",
        "polygon(66.66% 0, 100% 0, 100% 50%)",
        "polygon(66.66% 0, 100% 50%, 66.66% 50%)",
        "polygon(0 50%, 33.34% 50%, 0 100%)",
        "polygon(33.34% 50%, 33.34% 100%, 0 100%)",
        "polygon(33.33% 50%, 66.67% 50%, 33.33% 100%)",
        "polygon(66.67% 50%, 66.67% 100%, 33.33% 100%)",
        "polygon(66.66% 50%, 100% 50%, 100% 100%)",
        "polygon(66.66% 50%, 100% 100%, 66.66% 100%)"
    ];
    var emitterAnchors = [
        { x: 61, y: 13 },
        { x: 61, y: 14 },
        { x: 61, y: 13 },
        { x: 60, y: 13 },
        { x: 60, y: 13 },
        { x: 60, y: 14 },
        { x: 59, y: 13 },
        { x: 59, y: 14 }
    ];

    function loadImage(path) {
        var image = new Image();
        image.decoding = "async";
        image.src = path;
        return image;
    }

    var sprites = {
        walk: null,
        death: null
    };

    function loadEncounterSprites() {
        if (!sprites.walk) {
            sprites.walk = loadImage(
                "/Images/Game/Super-Frgmnts/enemy-tall-gaunt-alien-walk-sheet-v1.png"
            );
        }
        if (!sprites.death) {
            sprites.death = loadImage(
                "/Images/Game/Super-Frgmnts/enemy-seam-hunter-death-sheet-v1.png"
            );
        }
    }

    function clamp(value, minimum, maximum) {
        return Math.min(maximum, Math.max(minimum, value));
    }

    function setStatus(message, meter) {
        statusText.textContent = message;
        if (meter) meterText.textContent = meter;
    }

    function resizeCanvas() {
        deviceScale = Math.min(2, Math.max(1, window.devicePixelRatio || 1));
        canvas.width = Math.round(window.innerWidth * deviceScale);
        canvas.height = Math.round(window.innerHeight * deviceScale);
        context.setTransform(deviceScale, 0, 0, deviceScale, 0, 0);
        context.imageSmoothingEnabled = false;
    }

    function runnerPosition() {
        if (window.arynPageRunner && typeof window.arynPageRunner.position === "function") {
            return window.arynPageRunner.position();
        }
        var rect = document.querySelector(".pixel-runner").getBoundingClientRect();
        return {
            x: rect.left,
            top: rect.top,
            feetY: rect.bottom,
            width: rect.width || 96,
            facing: 1,
            motion: "idle"
        };
    }

    function emitterPoint(now) {
        var runner = runnerPosition();
        var frame = Math.floor(now / (1000 / 12)) % emitterAnchors.length;
        var anchor = emitterAnchors[frame];
        var anchorX = runner.facing < 0 ? 112 - anchor.x : anchor.x;
        return {
            x: runner.x + anchorX / 112 * runner.width,
            y: runner.top + anchor.y / 112 * runner.width
        };
    }

    function enemyCenter() {
        if (!encounter) return { id: "seam-hunter", x: window.innerWidth * 0.72, y: window.innerHeight * 0.58 };
        return {
            id: "seam-hunter",
            x: encounter.enemy.x,
            y: encounter.enemy.feetY - encounter.enemy.size * 0.54
        };
    }

    function chasePoint() {
        var target = enemyCenter();
        if (!encounter) return target;
        var gap = Math.min(150, Math.max(86, window.innerWidth * 0.115));
        return {
            id: "seam-hunter-chase-line",
            x: clamp(target.x - encounter.enemy.facing * gap, 32, window.innerWidth - 32),
            y: target.y
        };
    }

    function copyCanvasPixels(source, clone) {
        var sourceCanvases = [];
        var cloneCanvases = [];
        if (source instanceof HTMLCanvasElement) sourceCanvases.push(source);
        if (clone instanceof HTMLCanvasElement) cloneCanvases.push(clone);
        source.querySelectorAll("canvas").forEach(function (item) {
            sourceCanvases.push(item);
        });
        clone.querySelectorAll("canvas").forEach(function (item) {
            cloneCanvases.push(item);
        });
        sourceCanvases.forEach(function (sourceCanvas, index) {
            var cloneCanvas = cloneCanvases[index];
            if (!cloneCanvas) return;
            try {
                var still = document.createElement("img");
                still.src = sourceCanvas.toDataURL("image/png");
                still.alt = "";
                still.style.position = "relative";
                still.style.zIndex = "1";
                still.style.display = "block";
                still.style.width = "100%";
                still.style.height = "100%";
                cloneCanvas.replaceWith(still);
            } catch (error) {
                cloneCanvas.width = sourceCanvas.width;
                cloneCanvas.height = sourceCanvas.height;
                cloneCanvas.style.position = "relative";
                cloneCanvas.style.zIndex = "1";
                cloneCanvas.style.display = "block";
                cloneCanvas.style.width = "100%";
                cloneCanvas.style.height = "100%";
                var cloneContext = cloneCanvas.getContext("2d");
                try {
                    if (cloneContext) cloneContext.drawImage(sourceCanvas, 0, 0);
                } catch (drawError) {
                    // A blank clone is preferable to interrupting the reversible encounter.
                }
            }
        });
    }

    function cloneWithCanvasPixels(source) {
        var clone = source.cloneNode(true);
        copyCanvasPixels(source, clone);
        clone.querySelectorAll("[id]").forEach(function (element) {
            element.removeAttribute("id");
        });
        if (clone.hasAttribute && clone.hasAttribute("id")) clone.removeAttribute("id");
        clone.querySelectorAll("a, button, input, select, textarea, [tabindex]").forEach(function (element) {
            element.setAttribute("tabindex", "-1");
            if (element.matches("a")) element.removeAttribute("href");
        });
        clone.querySelectorAll("[aria-labelledby], [aria-describedby], [aria-controls], label[for]").forEach(function (element) {
            element.removeAttribute("aria-labelledby");
            element.removeAttribute("aria-describedby");
            element.removeAttribute("aria-controls");
            element.removeAttribute("for");
        });
        return clone;
    }

    function captureFacade() {
        facade.replaceChildren();
        var scene = document.createElement("main");
        scene.className = "page-destruction__scene";
        scene.setAttribute("aria-hidden", "true");
        scene.setAttribute("inert", "");
        facade.appendChild(scene);

        var selectors = [
            ".intro",
            ".preview-panel",
            ".controls-panel > .surprise-zone",
            ".controls-panel > .control-section",
            ".controls-panel > .action-stack",
            ".controls-panel > .system-message",
            ".controls-panel > .tiny-truth"
        ];
        var sources = Array.from(pageMain.querySelectorAll(selectors.join(",")));
        var fragments = sources.map(function (source, index) {
            var rect = source.getBoundingClientRect();
            if (
                rect.width < 24 ||
                rect.height < 20 ||
                rect.right < 0 ||
                rect.bottom < 0 ||
                rect.left > window.innerWidth ||
                rect.top > window.innerHeight
            ) return null;

            var fragment = document.createElement("div");
            fragment.className = "page-fragment";
            fragment.dataset.fragmentIndex = String(index);
            fragment.style.left = rect.left + "px";
            fragment.style.top = rect.top + "px";
            fragment.style.width = rect.width + "px";
            fragment.style.height = rect.height + "px";
            fragment.appendChild(cloneWithCanvasPixels(source));
            scene.appendChild(fragment);
            return {
                element: fragment,
                rect: {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                },
                destroyed: false
            };
        }).filter(Boolean);

        document.body.classList.add("page-destruction-facade-ready");
        return fragments;
    }

    function nextDamageTarget() {
        var candidates = encounter.fragments.filter(function (fragment) {
            return !fragment.destroyed;
        });
        if (!candidates.length) {
            encounter.damageCursor += 1;
            return null;
        }
        var index = (encounter.damageCursor * 5 + 2) % candidates.length;
        encounter.damageCursor += 1;
        return candidates[index];
    }

    function targetPoint(fragment) {
        if (!fragment) {
            return {
                x: window.innerWidth * (0.24 + (encounter.damageCursor % 4) * 0.16),
                y: window.innerHeight * (0.28 + (encounter.damageCursor % 3) * 0.16)
            };
        }
        var rect = fragment.rect;
        return {
            x: clamp(rect.left + rect.width * 0.52, 24, window.innerWidth - 24),
            y: clamp(rect.top + rect.height * 0.48, 70, window.innerHeight - 24)
        };
    }

    function shatterFragment(fragment, point) {
        if (!fragment || fragment.destroyed) return;
        fragment.destroyed = true;
        var source = fragment.element;
        var impactX = clamp((point.x - fragment.rect.left) / fragment.rect.width * 100, 0, 100);
        var impactY = clamp((point.y - fragment.rect.top) / fragment.rect.height * 100, 0, 100);

        shardClips.forEach(function (clip, index) {
            var shard = cloneWithCanvasPixels(source);
            var cell = Math.floor(index / 2);
            var column = cell % 3;
            var row = Math.floor(cell / 3);
            var columnDirection = column === 1 ? (index % 2 ? 1 : -1) : column - 1;
            var rowDirection = row === 0 ? -1 : 1;
            var force = 56 + index * 9 + encounter.damageCursor * 3;
            shard.className = "page-shard";
            shard.removeAttribute("data-fragment-index");
            shard.style.setProperty("--shard-clip", clip);
            shard.style.setProperty("--impact-x", impactX + "%");
            shard.style.setProperty("--impact-y", impactY + "%");
            shard.style.setProperty("--shard-x", columnDirection * force + "px");
            shard.style.setProperty("--shard-y", (rowDirection * force * 0.46 + 102 + index * 7) + "px");
            shard.style.setProperty("--shard-rotate", columnDirection * (24 + index * 7) + "deg");
            shard.style.setProperty("--shard-scale", String(0.38 + index % 3 * 0.055));
            shard.style.setProperty("--shard-duration", (reducedMotion ? 340 : 780 + index * 44) + "ms");
            source.parentNode.insertBefore(shard, source.nextSibling);
            window.setTimeout(function () {
                shard.remove();
            }, reducedMotion ? 420 : 1600);
        });

        source.classList.add("page-fragment--struck");
        window.setTimeout(function () {
            source.remove();
        }, 40);
        encounter.destroyedCount += 1;
        overlay.dataset.damageCount = String(encounter.destroyedCount);
    }

    function addBurst(x, y, color, amount) {
        for (var index = 0; index < amount; index += 1) {
            var angle = index / amount * Math.PI * 2 + encounter.particleSeed * 0.31;
            var speed = 48 + (index % 5) * 26;
            encounter.particles.push({
                kind: "spark",
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 34,
                size: 2 + index % 4,
                color: color,
                gravity: 220,
                grow: 0,
                life: 0.42 + (index % 4) * 0.09,
                maxLife: 0.42 + (index % 4) * 0.09
            });
        }
        encounter.particleSeed += 1;
    }

    function particleNoise(index, salt) {
        var raw = Math.sin((encounter.particleSeed + index * 1.73 + salt) * 12.9898) * 43758.5453;
        return raw - Math.floor(raw);
    }

    function addImpactCloud(x, y, lethal) {
        var debrisColors = ["#f2edf5", "#9eb0c7", "#4b5368", "#191c28", "#ff6b43"];
        var debrisCount = reducedMotion ? 7 : lethal ? 42 : 26;
        var dustCount = reducedMotion ? 3 : lethal ? 16 : 10;
        var smokeCount = reducedMotion ? 2 : lethal ? 12 : 7;
        var fireCount = reducedMotion ? 2 : lethal ? 18 : 8;

        for (var index = 0; index < debrisCount; index += 1) {
            var angle = particleNoise(index, 1) * Math.PI * 2;
            var speed = 70 + particleNoise(index, 2) * (lethal ? 270 : 185);
            var life = 0.7 + particleNoise(index, 3) * 0.75;
            encounter.particles.push({
                kind: "debris",
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 80,
                size: 1.5 + particleNoise(index, 4) * 4.5,
                color: debrisColors[index % debrisColors.length],
                gravity: 360,
                grow: -0.7,
                life: life,
                maxLife: life
            });
        }

        for (var dustIndex = 0; dustIndex < dustCount; dustIndex += 1) {
            var dustLife = 0.85 + particleNoise(dustIndex, 7) * 0.7;
            encounter.particles.push({
                kind: "dust",
                x: x + (particleNoise(dustIndex, 8) - 0.5) * 36,
                y: y + (particleNoise(dustIndex, 9) - 0.5) * 22,
                vx: (particleNoise(dustIndex, 10) - 0.5) * 72,
                vy: -24 - particleNoise(dustIndex, 11) * 42,
                size: 7 + particleNoise(dustIndex, 12) * 13,
                color: dustIndex % 2 ? "#c5b6a4" : "#7d7984",
                gravity: -4,
                grow: 13,
                life: dustLife,
                maxLife: dustLife
            });
        }

        for (var smokeIndex = 0; smokeIndex < smokeCount; smokeIndex += 1) {
            var smokeLife = 1.25 + particleNoise(smokeIndex, 14) * 1.05;
            encounter.particles.push({
                kind: "smoke",
                x: x + (particleNoise(smokeIndex, 15) - 0.5) * 24,
                y: y + (particleNoise(smokeIndex, 16) - 0.5) * 16,
                vx: (particleNoise(smokeIndex, 17) - 0.5) * 34,
                vy: -32 - particleNoise(smokeIndex, 18) * 38,
                size: 10 + particleNoise(smokeIndex, 19) * 17,
                color: smokeIndex % 2 ? "#252635" : "#10121b",
                gravity: -7,
                grow: 9,
                life: smokeLife,
                maxLife: smokeLife
            });
        }

        for (var fireIndex = 0; fireIndex < fireCount; fireIndex += 1) {
            var fireLife = 0.38 + particleNoise(fireIndex, 22) * 0.52;
            encounter.particles.push({
                kind: "fire",
                x: x + (particleNoise(fireIndex, 23) - 0.5) * (lethal ? 58 : 28),
                y: y + (particleNoise(fireIndex, 24) - 0.5) * 24,
                vx: (particleNoise(fireIndex, 25) - 0.5) * 90,
                vy: -55 - particleNoise(fireIndex, 26) * 90,
                size: 3 + particleNoise(fireIndex, 27) * 7,
                color: fireIndex % 3 === 0 ? "#fff2a8" : fireIndex % 2 ? "#ff9b38" : "#ff365f",
                gravity: -35,
                grow: -1.8,
                life: fireLife,
                maxLife: fireLife
            });
        }

        if (lethal) {
            encounter.particles.push({
                kind: "ring",
                x: x,
                y: y,
                vx: 0,
                vy: 0,
                size: 8,
                color: "#ecffff",
                gravity: 0,
                grow: 150,
                life: 0.6,
                maxLife: 0.6
            });
        }
        encounter.particleSeed += 3;
    }

    function shakePage() {
        document.body.classList.remove("page-destruction-impact");
        void document.body.offsetWidth;
        document.body.classList.add("page-destruction-impact");
        window.clearTimeout(shakeTimer);
        shakeTimer = window.setTimeout(function () {
            document.body.classList.remove("page-destruction-impact");
        }, 190);
    }

    function damagePage(fragment, point) {
        shatterFragment(fragment, point);
        addBurst(point.x, point.y, "#ff4c88", reducedMotion ? 5 : 16);
        addImpactCloud(point.x, point.y, false);
        shakePage();
        setStatus(
            "Miss // Scenery disintegrating",
            "Collateral damage // " + encounter.destroyedCount + " sections shattered"
        );
    }

    function createFallbackProjectile(origin, target) {
        var deltaX = target.x - origin.x;
        var deltaY = target.y - origin.y;
        var distance = Math.max(1, Math.hypot(deltaX, deltaY));
        return {
            x: origin.x,
            y: origin.y,
            velocityX: deltaX / distance * 860,
            velocityY: deltaY / distance * 860,
            lifetime: 2.2,
            trail: [],
            fallback: true
        };
    }

    function fireShot(hit, now) {
        var origin = emitterPoint(now);
        var damagedFragment = hit ? null : nextDamageTarget();
        var staticTarget = hit ? null : targetPoint(damagedFragment);
        var firstTarget = hit ? enemyCenter() : staticTarget;
        var direction = firstTarget.x < origin.x ? -1 : 1;
        var projectile;

        if (Beam && typeof Beam.createVolley === "function") {
            projectile = Beam.createVolley({
                x: origin.x,
                y: origin.y,
                target: firstTarget,
                direction: direction,
                idBase: 4000 + encounter.nextShot * 4
            })[0];
            projectile.velocityX *= hit ? 2.15 : 1.65;
            projectile.velocityY *= hit ? 2.15 : 1.65;
            projectile.lifetime = 2.2;
        } else {
            projectile = createFallbackProjectile(origin, firstTarget);
        }

        encounter.projectiles.push({
            projectile: projectile,
            hit: hit,
            final: hit,
            fragment: damagedFragment,
            staticTarget: staticTarget,
            done: false
        });
        overlay.dataset.shotCount = String(encounter.nextShot + 1);
        setStatus(
            "Pack fire // Shot " + (encounter.nextShot + 1),
            hit ? "Kill solution locked" : "Seam Hunter evading"
        );
        if (window.arynPageRunner) {
            window.arynPageRunner.setFiring(true);
            window.clearTimeout(firingTimer);
            firingTimer = window.setTimeout(function () {
                if (window.arynPageRunner) window.arynPageRunner.setFiring(false);
            }, 190);
        }
    }

    function projectileTarget(shot) {
        return shot.hit ? enemyCenter() : shot.staticTarget;
    }

    function updateProjectile(shot, delta) {
        var projectile = shot.projectile;
        var target = projectileTarget(shot);
        if (projectile.fallback) {
            projectile.trail.push({ x: projectile.x, y: projectile.y });
            if (projectile.trail.length > 10) projectile.trail.shift();
            projectile.x += projectile.velocityX * delta;
            projectile.y += projectile.velocityY * delta;
            projectile.lifetime -= delta;
        } else {
            Beam.updateProjectile(projectile, delta, target);
        }

        var distance = Math.hypot(projectile.x - target.x, projectile.y - target.y);
        if (distance > 28 && projectile.lifetime > 0) return;

        shot.done = true;
        if (shot.hit) {
            encounter.enemy.hits = 1;
            encounter.enemy.killed = true;
            encounter.enemy.dyingAt = encounter.canonicalElapsed;
            encounter.impactFlash = reducedMotion ? 0.16 : 0.38;
            addBurst(target.x, target.y, "#72fff0", reducedMotion ? 9 : 34);
            addImpactCloud(target.x, target.y, true);
            shakePage();
            setStatus("Shot 14 // Direct hit", "Seam Hunter // Eliminated");
        } else {
            damagePage(shot.fragment, target);
        }
    }

    function drawFallbackProjectile(projectile, finalShot) {
        context.save();
        context.globalCompositeOperation = "lighter";
        context.strokeStyle = "rgba(62, 231, 218, 0.72)";
        context.lineWidth = finalShot ? 7 : 3;
        context.shadowColor = "#43fff1";
        context.shadowBlur = reducedMotion ? 0 : 8;
        context.beginPath();
        projectile.trail.forEach(function (point, index) {
            if (index === 0) context.moveTo(point.x, point.y);
            else context.lineTo(point.x, point.y);
        });
        context.lineTo(projectile.x, projectile.y);
        context.stroke();
        context.fillStyle = "#fff";
        context.fillRect(
            projectile.x - (finalShot ? 12 : 7),
            projectile.y - (finalShot ? 4 : 2),
            finalShot ? 24 : 14,
            finalShot ? 8 : 4
        );
        context.restore();
    }

    function updateEnemy() {
        var enemy = encounter.enemy;
        if (enemy.dyingAt !== null) return;
        var elapsed = encounter.canonicalElapsed;
        var width = window.innerWidth;
        var routeIndex = 0;
        while (
            routeIndex < enemyRoute.length - 2 &&
            elapsed > enemyRoute[routeIndex + 1].time
        ) {
            routeIndex += 1;
        }
        var from = enemyRoute[routeIndex];
        var to = enemyRoute[Math.min(routeIndex + 1, enemyRoute.length - 1)];
        var progress = clamp((elapsed - from.time) / Math.max(0.01, to.time - from.time), 0, 1);
        var eased = progress * progress * (3 - 2 * progress);
        var targetX = width * (from.x + (to.x - from.x) * eased);
        targetX = clamp(targetX, enemy.size * 0.56, width - enemy.size * 0.56);
        var previousX = enemy.x;
        enemy.x = targetX;
        if (Math.abs(enemy.x - previousX) > 0.1) enemy.facing = enemy.x < previousX ? -1 : 1;
        var leap = 0;
        var leapHeight = 0;
        enemyLeapWindows.forEach(function (windowSpec) {
            if (elapsed < windowSpec.start || elapsed > windowSpec.end) return;
            var leapProgress = (elapsed - windowSpec.start) / (windowSpec.end - windowSpec.start);
            leap = Math.max(leap, Math.pow(Math.sin(leapProgress * Math.PI), 1.45));
            leapHeight = Math.max(
                leapHeight,
                Math.min(150, window.innerHeight * windowSpec.height)
            );
        });
        enemy.feetY = window.innerHeight * 0.725 - leap * leapHeight;
    }

    function drawEnemy() {
        var enemy = encounter.enemy;
        var dying = enemy.dyingAt !== null;
        var image = dying ? sprites.death : sprites.walk;
        var size = enemy.size;
        var drawWidth = dying ? size * 1.25 : size;
        var drawHeight = size;

        context.save();
        context.globalAlpha = dying
            ? Math.max(0.12, 1 - Math.max(0, encounter.canonicalElapsed - enemy.dyingAt - 1.8) / 1.1)
            : 1;
        context.fillStyle = "rgba(0, 0, 0, 0.48)";
        context.beginPath();
        context.ellipse(enemy.x, enemy.feetY - 3, size * 0.28, 7, 0, 0, Math.PI * 2);
        context.fill();
        context.translate(Math.round(enemy.x), Math.round(enemy.feetY));
        context.scale(enemy.facing, 1);
        context.shadowColor = dying ? "#ff3b76" : "rgba(92, 66, 255, 0.72)";
        context.shadowBlur = reducedMotion ? 0 : 12;

        if (image.complete && image.naturalWidth) {
            var frame;
            var columns;
            var frameWidth;
            var frameHeight;
            if (dying) {
                frame = Math.min(24, Math.floor((encounter.canonicalElapsed - enemy.dyingAt) / 0.107));
                columns = 5;
                frameWidth = 280;
                frameHeight = 223;
            } else {
                frame = Math.floor(encounter.canonicalElapsed / 0.052) % 36;
                columns = 6;
                frameWidth = 128;
                frameHeight = 128;
            }
            context.drawImage(
                image,
                frame % columns * frameWidth,
                Math.floor(frame / columns) * frameHeight,
                frameWidth,
                frameHeight,
                -drawWidth / 2,
                -drawHeight,
                drawWidth,
                drawHeight
            );
        } else {
            context.fillStyle = "#402a79";
            context.fillRect(-size * 0.18, -size * 0.82, size * 0.36, size * 0.72);
            context.fillStyle = "#ff4f9a";
            context.fillRect(-size * 0.12, -size * 0.72, size * 0.24, size * 0.12);
        }
        context.restore();
    }

    function updateParticles(delta) {
        encounter.particles.forEach(function (particle) {
            particle.life -= delta;
            particle.vy += (particle.gravity === undefined ? 220 : particle.gravity) * delta;
            particle.x += particle.vx * delta;
            particle.y += particle.vy * delta;
            particle.size = Math.max(0.5, particle.size + (particle.grow || 0) * delta);
        });
        encounter.particles = encounter.particles.filter(function (particle) {
            return particle.life > 0;
        });
        encounter.impactFlash = Math.max(0, encounter.impactFlash - delta);
    }

    function drawParticles() {
        context.save();
        encounter.particles.forEach(function (particle) {
            var lifeRatio = Math.max(0, particle.life / particle.maxLife);
            context.globalCompositeOperation = (
                particle.kind === "smoke" || particle.kind === "dust" || particle.kind === "debris"
            ) ? "source-over" : "lighter";
            context.globalAlpha = lifeRatio * (
                particle.kind === "smoke" ? 0.54 : particle.kind === "dust" ? 0.42 : 1
            );
            context.fillStyle = particle.color;
            context.shadowColor = particle.color;
            context.shadowBlur = reducedMotion || particle.kind === "smoke" || particle.kind === "dust" ? 0 : 6;

            if (particle.kind === "ring") {
                context.strokeStyle = particle.color;
                context.lineWidth = Math.max(1, 5 * lifeRatio);
                context.beginPath();
                context.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                context.stroke();
            } else if (particle.kind === "smoke" || particle.kind === "dust") {
                var block = Math.max(2, Math.round(particle.size / 3));
                context.fillRect(particle.x - block, particle.y - block, block * 2, block * 2);
                context.fillRect(particle.x - particle.size * 0.5, particle.y, particle.size, block);
                context.fillRect(particle.x, particle.y - particle.size * 0.5, block, particle.size);
            } else if (particle.kind === "debris") {
                context.fillRect(
                    Math.round(particle.x),
                    Math.round(particle.y),
                    Math.max(1, Math.round(particle.size * 1.7)),
                    Math.max(1, Math.round(particle.size * 0.72))
                );
            } else {
                context.fillRect(particle.x, particle.y, particle.size, particle.size);
            }
        });
        context.restore();
    }

    function drawImpactFlash() {
        if (encounter.impactFlash <= 0) return;
        context.save();
        context.globalCompositeOperation = "screen";
        context.globalAlpha = Math.min(0.46, encounter.impactFlash * 1.2);
        context.fillStyle = "#b9ffff";
        context.fillRect(0, 0, window.innerWidth, window.innerHeight);
        context.restore();
    }

    function drawProjectiles() {
        encounter.projectiles.forEach(function (shot) {
            if (shot.projectile.fallback) {
                drawFallbackProjectile(shot.projectile, shot.final);
            } else {
                Beam.drawProjectile(context, shot.projectile, {
                    visualScale: shot.final ? 1.5 : 0.82,
                    softShadows: !reducedMotion
                });
            }
        });
    }

    function obliterateRemainingFacade() {
        if (!encounter) return;
        encounter.fragments.forEach(function (fragment, index) {
            if (fragment.destroyed) return;
            shatterFragment(fragment, {
                x: fragment.rect.left + fragment.rect.width * (0.35 + index % 3 * 0.15),
                y: fragment.rect.top + fragment.rect.height * 0.5
            });
        });
    }

    function completeEncounter() {
        if (!encounter || encounter.complete) return;
        encounter.complete = true;
        obliterateRemainingFacade();
        overlay.dataset.encounterState = "complete";
        document.body.classList.add("page-destruction-complete");
        setStatus(
            "Target eliminated // Page also eliminated",
            "Collateral damage // Unacceptable"
        );
        restoreButton.hidden = false;
        if (window.arynPageRunner) window.arynPageRunner.disengage();
        restoreButton.focus({ preventScroll: true });
    }

    function engageRunner() {
        if (
            !encounter ||
            encounter.runnerEngaged ||
            !window.arynPageRunner
        ) return;
        window.arynPageRunner.engage(function () {
            return chasePoint();
        });
        encounter.runnerEngaged = true;
    }

    function tick(now) {
        if (!encounter || encounter.complete) return;
        engageRunner();
        var realDelta = Math.min(0.04, Math.max(0, (now - encounter.lastFrame) / 1000));
        encounter.lastFrame = now;
        encounter.canonicalElapsed = (now - encounter.startedAt) / 1000 / encounter.timeScale;
        updateEnemy();

        while (
            encounter.nextJumpCue < runnerJumpTimes.length &&
            encounter.canonicalElapsed >= runnerJumpTimes[encounter.nextJumpCue]
        ) {
            if (window.arynPageRunner && typeof window.arynPageRunner.cueJump === "function") {
                window.arynPageRunner.cueJump(encounter.nextJumpCue % 2 ? 1.12 : 1);
            }
            encounter.nextJumpCue += 1;
        }

        while (
            encounter.nextShot < shotTimes.length &&
            encounter.canonicalElapsed >= shotTimes[encounter.nextShot]
        ) {
            fireShot(encounter.nextShot === killShotIndex, now);
            encounter.nextShot += 1;
        }

        encounter.projectiles.forEach(function (shot) {
            if (!shot.done) updateProjectile(shot, realDelta / encounter.timeScale);
        });
        encounter.projectiles = encounter.projectiles.filter(function (shot) {
            return !shot.done;
        });
        updateParticles(realDelta / encounter.timeScale);

        context.clearRect(0, 0, window.innerWidth, window.innerHeight);
        drawEnemy();
        drawProjectiles();
        drawParticles();
        drawImpactFlash();

        var deathFinished = encounter.enemy.dyingAt !== null &&
            encounter.canonicalElapsed >= encounter.enemy.dyingAt + 2.9;
        if (encounter.canonicalElapsed >= 26 || deathFinished) {
            completeEncounter();
            return;
        }
        animationFrame = window.requestAnimationFrame(tick);
    }

    function beginEncounter() {
        if (!preparing || encounter) return;
        preparing = false;
        window.scrollTo({ top: 0, left: 0, behavior: "auto" });
        loadEncounterSprites();
        resizeCanvas();
        restoreButton.hidden = true;
        overlay.hidden = false;
        overlay.dataset.encounterState = "active";
        overlay.dataset.shotCount = "0";
        overlay.dataset.damageCount = "0";
        var fragments = captureFacade();
        var startedAt = performance.now();
        encounter = {
            startedAt: startedAt,
            lastFrame: startedAt,
            canonicalElapsed: 0,
            timeScale: reducedMotion ? 0.4 : 1,
            nextShot: 0,
            nextJumpCue: 0,
            damageCursor: 0,
            destroyedCount: 0,
            fragments: fragments,
            projectiles: [],
            particles: [],
            particleSeed: 1,
            impactFlash: 0,
            runnerEngaged: false,
            complete: false,
            originalScrollY: pendingScrollY,
            enemy: {
                x: window.innerWidth * enemyRoute[0].x,
                feetY: window.innerHeight * 0.725,
                size: clamp(window.innerWidth * 0.15, 112, 178),
                facing: -1,
                hits: 0,
                killed: false,
                dyingAt: null
            }
        };
        document.body.classList.add("page-destruction-active");
        document.body.classList.remove("page-destruction-complete");
        pageMain.setAttribute("inert", "");
        setStatus("Anomaly detected // Seam Hunter breach", "Aryn Sol-Mavi // Pack online");

        engageRunner();
        animationFrame = window.requestAnimationFrame(tick);
    }

    function startEncounter() {
        if (encounter || preparing) return;
        preparing = true;
        pendingScrollY = window.scrollY;
        trigger.disabled = true;
        window.scrollTo({
            top: 0,
            left: 0,
            behavior: reducedMotion ? "auto" : "smooth"
        });
        window.clearTimeout(startTimer);
        startTimer = window.setTimeout(beginEncounter, reducedMotion ? 40 : 560);
    }

    function restoreTimeline() {
        if (preparing && !encounter) {
            preparing = false;
            window.clearTimeout(startTimer);
            trigger.disabled = false;
            window.scrollTo({ top: pendingScrollY, left: 0, behavior: "auto" });
            trigger.focus({ preventScroll: true });
            return;
        }
        if (!encounter) return;
        var restoreScrollY = encounter.originalScrollY;
        window.cancelAnimationFrame(animationFrame);
        window.clearTimeout(startTimer);
        window.clearTimeout(firingTimer);
        window.clearTimeout(shakeTimer);
        if (window.arynPageRunner) window.arynPageRunner.disengage();
        context.clearRect(0, 0, window.innerWidth, window.innerHeight);
        document.body.classList.remove(
            "page-destruction-active",
            "page-destruction-impact",
            "page-destruction-complete",
            "page-destruction-facade-ready"
        );
        overlay.hidden = true;
        facade.replaceChildren();
        pageMain.removeAttribute("inert");
        delete overlay.dataset.encounterState;
        delete overlay.dataset.shotCount;
        delete overlay.dataset.damageCount;
        encounter = null;
        trigger.disabled = false;
        window.scrollTo({ top: restoreScrollY, left: 0, behavior: "auto" });
        trigger.focus({ preventScroll: true });
    }

    trigger.addEventListener("click", startEncounter);
    restoreButton.addEventListener("click", restoreTimeline);
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && (encounter || preparing)) restoreTimeline();
    });
    window.addEventListener("resize", function () {
        if (!encounter) return;
        resizeCanvas();
        encounter.enemy.size = clamp(window.innerWidth * 0.15, 112, 178);
        encounter.enemy.x = clamp(
            encounter.enemy.x,
            encounter.enemy.size * 0.56,
            window.innerWidth - encounter.enemy.size * 0.56
        );
    }, { passive: true });

    window.OTWPageDestruction = Object.freeze({
        start: startEncounter,
        restore: restoreTimeline,
        state: function () {
            if (preparing) return "preparing";
            if (!encounter) return "idle";
            return encounter.complete ? "complete" : "active";
        }
    });
})();
