#!/usr/bin/env python3
"""Static controller-completeness checks for Super Frgmnts selectable UI."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "super_frgmnts.html"


def require(source: str, token: str, label: str) -> None:
    if token not in source:
        raise AssertionError(f"Missing {label}: {token}")


def reject(source: str, token: str, label: str) -> None:
    if token in source:
        raise AssertionError(f"Retired {label} is still present: {token}")


def main() -> None:
    source = HTML.read_text(encoding="utf-8")

    required_buttons = (
        "pauseButton",
        "soundButton",
        "restartButton",
        "masterResetButton",
        "signalBootButton",
        "titleStartButton",
        "titleDifficultyButton",
        "startButton",
        "startOverButton",
        "pauseResumeButton",
        "pausePackButton",
        "pauseSoundButton",
        "pauseRestartButton",
        "pauseTitleButton",
        "packBackButton",
        "packResumeButton",
        "dialogueContinue",
        "dialogueSkip",
        "dialogueSkipScene",
        "dialogueReturn",
        "bossIntroSkip",
        "episodeBridgeSkip",
    )
    for button_id in required_buttons:
        require(source, f'id="{button_id}"', f"#{button_id} button")

    contracts = (
        (
            "signalBootButton.click();",
            "Cross activation for the Load Game gate",
        ),
        (
            'toggleHardMode();',
            "Triangle difficulty toggle",
        ),
        (
            'focusDialogueSkipControl(dialogueReturn);',
            "safe dialogue-skip default",
        ),
        (
            'moveDialogueSkipFocus(menuDirection);',
            "dialogue-skip D-pad / stick navigation",
        ),
        (
            'dialogueSkipControl.click();',
            "Cross confirmation of the highlighted dialogue choice",
        ),
        (
            'moveMessageCardFocus(menuDirection);',
            "generic two-button card navigation",
        ),
        (
            'messageControl.click();',
            "generic card confirmation",
        ),
        (
            'startOverButton.click();',
            "Circle route-card cancellation",
        ),
        (
            'soundButton.click();',
            "Pause-menu sound toggle",
        ),
        (
            'movePauseMenuFocus(menuDirection);',
            "Pause / PACK navigation",
        ),
        (
            'restartPauseCheckpoint',
            "Pause-menu checkpoint restart",
        ),
        (
            'masterResetToTitle',
            "Pause-menu title reset",
        ),
        (
            'completeWoundBossIntro(true);',
            "boss-interstitial skip",
        ),
        (
            'completeEpisodeBridge();',
            "episode-bridge skip",
        ),
        (
            'advancePrismInstallCinematic(false);',
            "Prism comic advance",
        ),
        (
            'advancePrismInstallCinematic(true);',
            "Prism comic skip",
        ),
        (
            '? "dialogue-skip-confirm"',
            "render_game_to_text dialogue selection state",
        ),
        (
            '? "message"',
            "render_game_to_text message selection state",
        ),
    )
    for token, label in contracts:
        require(source, token, label)

    if source.count('data-pack-module="') != 5:
        raise AssertionError("Expected exactly five PACK module buttons")
    require(source, 'id="directionPad"', "touch direction control")
    require(source, 'data-control="shoot"', "touch fire control")
    require(source, 'data-control="jump"', "touch jump control")

    require(
        source,
        '<span><kbd>D-PAD</kbd> Select</span>',
        "visible dialogue-skip controller legend",
    )
    require(
        source,
        "Cross / Options / Enter",
        "visible Seam Hunter interstitial controller legend",
    )
    require(
        source,
        '"Sound // " + (soundOn ? "On" : "Off")',
        "live pause sound label",
    )

    reject(
        source,
        "Click Load Game once to allow browser audio",
        "pointer-only Load Game instruction",
    )
    reject(
        source,
        'else if (confirmPressed) {\n                        if (dialogueSkipOpen) {\n                            closeDialogueSkipConfirmation();',
        "Cross-as-back dialogue behavior",
    )
    reject(
        source,
        '!messageCard.hidden &&\n                    !startButton.disabled',
        "primary-only message-card controller gate",
    )

    print("Super Frgmnts controller selection audit: PASS")
    print(f"  audited named buttons: {len(required_buttons)}")
    print("  audited PACK module buttons: 5")
    print("  audited touch gameplay controls: 3")
    print(f"  controller contracts: {len(contracts)}")


if __name__ == "__main__":
    main()
