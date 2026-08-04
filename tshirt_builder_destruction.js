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

    var shotTimes = [2.3, 3.75, 5.2, 6.65, 8.1, 9.55, 11.0, 12.45, 13.9, 15.35, 17.0, 18.65, 20.3];
    var hitShotIndexes = new Set([10, 11, 12]);
    var shardClips = [
        "polygon(0 0, 50% 0, 0 50%)",
        "polygon(50% 0, 50% 50%, 0 50%)",
        "polygon(50% 0, 100% 0, 100% 50%)",
        "polygon(50% 0, 100% 50%, 50% 50%)",
        "polygon(0 50%, 50% 50%, 0 100%)",
        "polygon(50% 50%, 50% 100%, 0 100%)",
        "polygon(50% 50%, 100% 50%, 100% 100%)",
        "polygon(50% 50%, 100% 100%, 50% 100%)"
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
            cloneCanvas.width = sourceCanvas.width;
            cloneCanvas.height = sourceCanvas.height;
            cloneCanvas.style.position = "relative";
            cloneCanvas.style.zIndex = "1";
            cloneCanvas.style.display = "block";
            cloneCanvas.style.width = "100%";
            cloneCanvas.style.height = "100%";
            var cloneContext = cloneCanvas.getContext("2d");
            if (!cloneContext) return;
            try {
                cloneContext.drawImage(sourceCanvas, 0, 0);
            } catch (error) {
                // The façade remains usable even if an optional canvas cannot be copied.
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
            var columnDirection = index % 4 < 2 ? -1 : 1;
            var rowDirection = index < 4 ? -1 : 1;
            var force = 68 + index * 13 + encounter.damageCursor * 4;
            shard.className = "page-shard";
            shard.removeAttribute("data-fragment-index");
            shard.style.setProperty("--shard-clip", clip);
            shard.style.setProperty("--impact-x", impactX + "%");
            shard.style.setProperty("--impact-y", impactY + "%");
            shard.style.setProperty("--shard-x", columnDirection * force + "px");
            shard.style.setProperty("--shard-y", (rowDirection * force * 0.52 + 118 + index * 9) + "px");
            shard.style.setProperty("--shard-rotate", columnDirection * (18 + index * 9) + "deg");
            shard.style.setProperty("--shard-scale", String(0.62 + index % 3 * 0.07));
            shard.style.setProperty("--shard-duration", (reducedMotion ? 340 : 900 + index * 58) + "ms");
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
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 34,
                size: 2 + index % 4,
                color: color,
                life: 0.42 + (index % 4) * 0.09,
                maxLife: 0.42 + (index % 4) * 0.09
            });
        }
        encounter.particleSeed += 1;
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
            projectile.velocityX *= 1.65;
            projectile.velocityY *= 1.65;
            projectile.lifetime = 2.2;
        } else {
            projectile = createFallbackProjectile(origin, firstTarget);
        }

        encounter.projectiles.push({
            projectile: projectile,
            hit: hit,
            fragment: damagedFragment,
            staticTarget: staticTarget,
            done: false
        });
        overlay.dataset.shotCount = String(encounter.nextShot + 1);
        setStatus(
            "Pack fire // Shot " + (encounter.nextShot + 1),
            hit ? "Tracking solution locked" : "Seam Hunter evading"
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
            encounter.enemy.hits += 1;
            addBurst(target.x, target.y, "#72fff0", reducedMotion ? 7 : 22);
            shakePage();
            if (encounter.enemy.hits >= 3) {
                encounter.enemy.dyingAt = encounter.canonicalElapsed;
                setStatus("Direct hit // Target collapsing", "Seam Hunter // Integrity zero");
            } else {
                setStatus(
                    "Direct hit // " + encounter.enemy.hits + " of 3",
                    "Seam Hunter // Integrity " + (3 - encounter.enemy.hits)
                );
            }
        } else {
            damagePage(shot.fragment, target);
        }
    }

    function drawFallbackProjectile(projectile) {
        context.save();
        context.globalCompositeOperation = "lighter";
        context.strokeStyle = "rgba(62, 231, 218, 0.72)";
        context.lineWidth = 3;
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
        context.fillRect(projectile.x - 7, projectile.y - 2, 14, 4);
        context.restore();
    }

    function updateEnemy(delta) {
        var enemy = encounter.enemy;
        if (enemy.dyingAt !== null) return;
        var elapsed = encounter.canonicalElapsed;
        var width = window.innerWidth;
        var route = [0.78, 0.14, 0.88, 0.26, 0.72, 0.09, 0.91, 0.33, 0.67, 0.18];
        var segmentDuration = 2.08;
        var routeElapsed = Math.max(0, elapsed - 0.45);
        var segment = Math.floor(routeElapsed / segmentDuration);
        var progress = clamp((routeElapsed % segmentDuration) / segmentDuration, 0, 1);
        var eased = progress * progress * (3 - 2 * progress);
        var from = segment === 0 ? 1.08 : route[(segment - 1) % route.length];
        var to = route[segment % route.length];
        var targetX = width * (from + (to - from) * eased);
        targetX = clamp(targetX, enemy.size * 0.56, width - enemy.size * 0.56);
        var previousX = enemy.x;
        enemy.x = targetX;
        if (Math.abs(enemy.x - previousX) > 0.1) enemy.facing = enemy.x < previousX ? -1 : 1;
        var leap = Math.pow(Math.sin(progress * Math.PI), 1.7);
        var leapHeight = segment % 2 === 0
            ? Math.min(92, window.innerHeight * 0.16)
            : Math.min(138, window.innerHeight * 0.23);
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
            particle.vy += 220 * delta;
            particle.x += particle.vx * delta;
            particle.y += particle.vy * delta;
        });
        encounter.particles = encounter.particles.filter(function (particle) {
            return particle.life > 0;
        });
    }

    function drawParticles() {
        context.save();
        context.globalCompositeOperation = "lighter";
        encounter.particles.forEach(function (particle) {
            context.globalAlpha = Math.max(0, particle.life / particle.maxLife);
            context.fillStyle = particle.color;
            context.shadowColor = particle.color;
            context.shadowBlur = reducedMotion ? 0 : 6;
            context.fillRect(particle.x, particle.y, particle.size, particle.size);
        });
        context.restore();
    }

    function drawProjectiles() {
        encounter.projectiles.forEach(function (shot) {
            if (shot.projectile.fallback) {
                drawFallbackProjectile(shot.projectile);
            } else {
                Beam.drawProjectile(context, shot.projectile, {
                    visualScale: 0.82,
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
            return enemyCenter();
        });
        encounter.runnerEngaged = true;
    }

    function tick(now) {
        if (!encounter || encounter.complete) return;
        engageRunner();
        var realDelta = Math.min(0.04, Math.max(0, (now - encounter.lastFrame) / 1000));
        encounter.lastFrame = now;
        encounter.canonicalElapsed = (now - encounter.startedAt) / 1000 / encounter.timeScale;
        updateEnemy(realDelta / encounter.timeScale);

        while (
            encounter.nextShot < shotTimes.length &&
            encounter.canonicalElapsed >= shotTimes[encounter.nextShot]
        ) {
            fireShot(hitShotIndexes.has(encounter.nextShot), now);
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
            damageCursor: 0,
            destroyedCount: 0,
            fragments: fragments,
            projectiles: [],
            particles: [],
            particleSeed: 1,
            runnerEngaged: false,
            complete: false,
            originalScrollY: pendingScrollY,
            enemy: {
                x: window.innerWidth + 180,
                feetY: window.innerHeight * 0.725,
                size: clamp(window.innerWidth * 0.15, 112, 178),
                facing: -1,
                hits: 0,
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
