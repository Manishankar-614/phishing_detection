(function () {

    "use strict";


    // ============================================================
    // CONFIGURATION
    // ============================================================

    const HOST_ID =
        "phishing-ai-warning-host";


    const WARNING_THRESHOLD =
        0.70;


    const DISMISS_KEY =
        "phishing_ai_warning_dismissed";


    let currentUrl =
        window.location.href;


    // ============================================================
    // INITIAL CHECK
    // ============================================================

    loadLatestResult();


    // ============================================================
    // STORAGE LISTENER
    // ============================================================

    if (
        chrome.storage &&
        chrome.storage.onChanged
    ) {

        chrome.storage.onChanged.addListener(
            (
                changes,
                areaName
            ) => {

                if (
                    areaName !== "local"
                ) {

                    return;

                }


                if (
                    changes.latestPhishingResult
                ) {

                    const newResult =
                        changes
                            .latestPhishingResult
                            .newValue;


                    if (
                        newResult
                    ) {

                        showWarning(
                            newResult
                        );

                    }

                }


                if (
                    changes.latestAnalyzedUrl
                ) {

                    loadLatestResult();

                }

            }
        );

    }


    // ============================================================
    // HANDLE SPA URL CHANGES
    // ============================================================

    function detectUrlChange() {

        const newUrl =
            window.location.href;


        if (
            newUrl !==
            currentUrl
        ) {

            currentUrl =
                newUrl;


            clearWarningState();


            setTimeout(
                () => {

                    loadLatestResult();

                },
                500
            );

        }

    }


    setInterval(
        detectUrlChange,
        500
    );


    // ============================================================
    // LOAD LATEST RESULT
    // ============================================================

    function loadLatestResult() {

        chrome.storage.local.get(
            [
                "latestPhishingResult",
                "latestAnalyzedUrl"
            ],
            (data) => {

                if (
                    chrome.runtime.lastError
                ) {

                    console.error(
                        "Phishing warning storage error:",
                        chrome.runtime.lastError
                    );

                    return;

                }


                const result =
                    data.latestPhishingResult;


                const analyzedUrl =
                    data.latestAnalyzedUrl;


                if (
                    !result
                ) {

                    clearWarningState();

                    return;

                }


                // ------------------------------------------------
                // NEVER USE A RESULT FROM ANOTHER PAGE
                // ------------------------------------------------

                if (
                    analyzedUrl &&
                    !urlsMatch(
                        analyzedUrl,
                        window.location.href
                    )
                ) {

                    clearWarningState();

                    return;

                }


                showWarning(
                    result
                );

            }
        );

    }


    // ============================================================
    // URL MATCHING
    // ============================================================

    function urlsMatch(
        analyzedUrl,
        currentPageUrl
    ) {

        try {

            const a =
                new URL(
                    analyzedUrl
                );


            const b =
                new URL(
                    currentPageUrl
                );


            return (

                a.origin ===
                b.origin

                &&

                a.pathname ===
                b.pathname

                &&

                a.search ===
                b.search

                &&

                a.hash ===
                b.hash

            );

        }

        catch {

            return (
                analyzedUrl ===
                currentPageUrl
            );

        }

    }


    // ============================================================
    // GET RISK SCORE
    // ============================================================

    function getRiskScore(
        risk
    ) {

        if (
            !risk
        ) {

            return null;

        }


        let score =
            Number(
                risk.risk_score
            );


        if (
            Number.isFinite(
                score
            )
        ) {

            if (
                score > 1
            ) {

                score =
                    score / 100;

            }


            return Math.max(
                0,
                Math.min(
                    1,
                    score
                )
            );

        }


        score =
            Number(
                risk.risk_percentage
            );


        if (
            Number.isFinite(
                score
            )
        ) {

            if (
                score > 1
            ) {

                score =
                    score / 100;

            }


            return Math.max(
                0,
                Math.min(
                    1,
                    score
                )
            );

        }


        return null;

    }


    // ============================================================
    // GET DISMISSED URL
    // ============================================================

    function getDismissedUrl() {

        try {

            return sessionStorage.getItem(
                DISMISS_KEY
            );

        }

        catch {

            return null;

        }

    }


    // ============================================================
    // CHECK DISMISSED
    // ============================================================

    function isWarningDismissedForCurrentPage() {

        const dismissedUrl =
            getDismissedUrl();


        if (
            !dismissedUrl
        ) {

            return false;

        }


        return urlsMatch(
            dismissedUrl,
            window.location.href
        );

    }


    // ============================================================
    // SAVE DISMISSAL
    // ============================================================

    function dismissWarningForCurrentPage() {

        try {

            sessionStorage.setItem(
                DISMISS_KEY,
                window.location.href
            );

        }

        catch {

            // Ignore storage restrictions.

        }

    }


    // ============================================================
    // CLEAR DISMISSAL
    // ============================================================

    function clearDismissal() {

        try {

            sessionStorage.removeItem(
                DISMISS_KEY
            );

        }

        catch {

            // Ignore storage restrictions.

        }

    }


    // ============================================================
    // CLEAR WARNING STATE
    // ============================================================

    function clearWarningState() {

        chrome.storage.local.set({
            warningActive:
                false
        });


        removeWarning();

    }


    // ============================================================
    // SHOW WARNING
    // ============================================================

    function showWarning(
        response
    ) {

        const result =
            response?.result ||
            response;


        const risk =
            result?.risk;


        const explanation =
            result?.explanation;


        if (
            !risk
        ) {

            return;

        }


        const riskScore =
            getRiskScore(
                risk
            );


        if (
            riskScore === null
        ) {

            return;

        }


        // --------------------------------------------------------
        // ONLY HIGH-RISK PAGES ARE BLOCKED
        // --------------------------------------------------------

        if (
            riskScore <
            WARNING_THRESHOLD
        ) {

            clearWarningState();

            return;

        }


        // --------------------------------------------------------
        // CONTINUE ANYWAY WAS SELECTED FOR THIS PAGE
        // --------------------------------------------------------

        if (
            isWarningDismissedForCurrentPage()
        ) {

            chrome.storage.local.set({
                warningActive:
                    false
            });


            removeWarning();

            return;

        }


        // --------------------------------------------------------
        // MARK WARNING ACTIVE
        // --------------------------------------------------------

        chrome.storage.local.set({
            warningActive:
                true
        });


        // --------------------------------------------------------
        // PREVENT DUPLICATE WARNING
        // --------------------------------------------------------

        if (
            document.getElementById(
                HOST_ID
            )
        ) {

            return;

        }


        // ========================================================
        // SHADOW DOM HOST
        // ========================================================

        const host =
            document.createElement(
                "div"
            );


        host.id =
            HOST_ID;


        host.style.position =
            "fixed";


        host.style.inset =
            "0";


        host.style.width =
            "100vw";


        host.style.height =
            "100vh";


        host.style.zIndex =
            "2147483647";


        host.style.pointerEvents =
            "auto";


        // ========================================================
        // SHADOW DOM
        // ========================================================

        const shadow =
            host.attachShadow({
                mode:
                    "closed"
            });


        // ========================================================
        // STYLE
        // ========================================================

        const style =
            document.createElement(
                "style"
            );


        style.textContent = `

            :host {
                all: initial;
            }

            * {
                box-sizing: border-box;
            }

            .warning-overlay {

                position: fixed;

                inset: 0;

                width: 100vw;

                height: 100vh;

                display: flex;

                align-items: center;

                justify-content: center;

                padding: 20px;

                background:
                    rgba(
                        3,
                        7,
                        18,
                        0.86
                    );

                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;

                color:
                    #e5e7eb;

                z-index:
                    2147483647;
            }


            .warning-card {

                width:
                    520px;

                max-width:
                    calc(
                        100vw - 40px
                    );

                max-height:
                    calc(
                        100vh - 40px
                    );

                overflow-y:
                    auto;

                padding:
                    30px;

                background:
                    #0b1220;

                border:
                    1px solid
                    #7f1d1d;

                border-radius:
                    18px;

                box-shadow:
                    0 30px 90px
                    rgba(
                        0,
                        0,
                        0,
                        0.65
                    );
            }


            .warning-icon {

                width:
                    60px;

                height:
                    60px;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;

                margin-bottom:
                    18px;

                border-radius:
                    14px;

                background:
                    #3b1118;

                font-size:
                    30px;
            }


            .warning-title {

                margin:
                    0 0 8px;

                color:
                    #fff1f2;

                font-size:
                    25px;

                font-weight:
                    700;
            }


            .warning-subtitle {

                margin:
                    0 0 22px;

                color:
                    #94a3b8;

                font-size:
                    14px;

                line-height:
                    1.55;
            }


            .risk-box {

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                padding:
                    16px;

                margin-bottom:
                    22px;

                background:
                    #160d12;

                border:
                    1px solid
                    #4c1d2b;

                border-radius:
                    11px;
            }


            .risk-label {

                color:
                    #94a3b8;

                font-size:
                    12px;

                font-weight:
                    500;
            }


            .risk-value {

                color:
                    #fda4af;

                font-size:
                    26px;

                font-weight:
                    700;
            }


            .section-title {

                margin:
                    0 0 11px;

                color:
                    #f8fafc;

                font-size:
                    15px;

                font-weight:
                    700;
            }


            .reason {

                margin-bottom:
                    8px;

                padding:
                    11px 12px;

                background:
                    #111827;

                border-left:
                    3px solid
                    #ef4444;

                border-radius:
                    6px;

                color:
                    #cbd5e1;

                font-size:
                    12px;

                line-height:
                    1.5;

                white-space:
                    pre-line;
            }


            .action {

                margin:
                    20px 0;

                padding:
                    13px;

                background:
                    #111827;

                border-radius:
                    8px;

                color:
                    #cbd5e1;

                font-size:
                    12px;

                line-height:
                    1.5;
            }


            .buttons {

                display:
                    flex;

                gap:
                    10px;

                margin-top:
                    5px;
            }


            button {

                flex:
                    1;

                min-height:
                    44px;

                border:
                    none;

                border-radius:
                    8px;

                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;

                font-size:
                    13px;

                font-weight:
                    700;

                cursor:
                    pointer;

                transition:
                    transform
                    0.15s ease,
                    opacity
                    0.15s ease;
            }


            button:hover {

                opacity:
                    0.92;

                transform:
                    translateY(-1px);
            }


            .back {

                background:
                    #5b1118;

                color:
                    #fecdd3;

                border:
                    1px solid
                    #991b1b;
            }


            .continue {

                background:
                    #172033;

                color:
                    #dbeafe;

                border:
                    1px solid
                    #334155;
            }


            .warning-footer {

                margin-top:
                    15px;

                text-align:
                    center;

                color:
                    #64748b;

                font-size:
                    10px;

                line-height:
                    1.4;
            }


            @media (
                max-width: 600px
            ) {

                .warning-overlay {

                    padding:
                        12px;
                }


                .warning-card {

                    width:
                        100%;

                    max-width:
                        100%;

                    padding:
                        22px;
                }


                .buttons {

                    flex-direction:
                        column;
                }

            }

        `;


        shadow.appendChild(
            style
        );


        // ========================================================
        // OVERLAY
        // ========================================================

        const overlay =
            document.createElement(
                "div"
            );


        overlay.className =
            "warning-overlay";


        // ========================================================
        // CARD
        // ========================================================

        const card =
            document.createElement(
                "div"
            );


        card.className =
            "warning-card";


        // ========================================================
        // ICON
        // ========================================================

        const icon =
            document.createElement(
                "div"
            );


        icon.className =
            "warning-icon";


        icon.textContent =
            "⚠️";


        // ========================================================
        // TITLE
        // ========================================================

        const title =
            document.createElement(
                "h1"
            );


        title.className =
            "warning-title";


        title.textContent =
            "Potential Phishing Threat";


        // ========================================================
        // SUBTITLE
        // ========================================================

        const subtitle =
            document.createElement(
                "p"
            );


        subtitle.className =
            "warning-subtitle";


        subtitle.textContent =
            "Our AI analysis detected suspicious characteristics on this webpage. Proceed with caution.";


        // ========================================================
        // RISK BOX
        // ========================================================

        const riskBox =
            document.createElement(
                "div"
            );


        riskBox.className =
            "risk-box";


        const riskLabel =
            document.createElement(
                "span"
            );


        riskLabel.className =
            "risk-label";


        riskLabel.textContent =
            "PHISHING RISK";


        const riskValue =
            document.createElement(
                "strong"
            );


        riskValue.className =
            "risk-value";


        riskValue.textContent =
            `${formatPercentage(
                risk.risk_percentage,
                riskScore
            )}%`;


        riskBox.appendChild(
            riskLabel
        );


        riskBox.appendChild(
            riskValue
        );


        // ========================================================
        // REASONS
        // ========================================================

        const reasonsSection =
            document.createElement(
                "div"
            );


        const reasonsTitle =
            document.createElement(
                "h2"
            );


        reasonsTitle.className =
            "section-title";


        reasonsTitle.textContent =
            "Why was this flagged?";


        reasonsSection.appendChild(
            reasonsTitle
        );


        const reasons =
            Array.isArray(
                explanation?.reasons
            )
                ? explanation.reasons
                : [];


        if (
            reasons.length === 0
        ) {

            const reason =
                document.createElement(
                    "div"
                );


            reason.className =
                "reason";


            reason.textContent =
                "The AI models detected characteristics associated with phishing.";


            reasonsSection.appendChild(
                reason
            );

        }

        else {

            reasons
                .slice(
                    0,
                    5
                )
                .forEach(
                    (item) => {

                        const reason =
                            document.createElement(
                                "div"
                            );


                        reason.className =
                            "reason";


                        if (
                            typeof item ===
                            "string"
                        ) {

                            reason.textContent =
                                item;

                        }

                        else {

                            const severity =
                                item?.severity
                                    ? String(
                                        item.severity
                                    ).toUpperCase()
                                    + " · "
                                    : "";


                            const source =
                                item?.source
                                    ? String(
                                        item.source
                                    ).toUpperCase()
                                    : "";


                            const message =
                                item?.reason ||
                                item?.message ||
                                "";


                            reason.textContent =
                                `${severity}${source}${severity || source ? "\n" : ""}${message}`;

                        }


                        reasonsSection.appendChild(
                            reason
                        );

                    }
                );

        }


        // ========================================================
        // RECOMMENDED ACTION
        // ========================================================

        const action =
            document.createElement(
                "div"
            );


        action.className =
            "action";


        action.textContent =
            risk.recommended_action ||
            "Do not enter passwords, OTPs, banking information or other sensitive information on this page.";


        // ========================================================
        // BUTTONS
        // ========================================================

        const buttons =
            document.createElement(
                "div"
            );


        buttons.className =
            "buttons";


        const backButton =
            document.createElement(
                "button"
            );


        backButton.className =
            "back";


        backButton.textContent =
            "Go Back";


        const continueButton =
            document.createElement(
                "button"
            );


        continueButton.className =
            "continue";


        continueButton.textContent =
            "Continue Anyway";


        // ========================================================
        // GO BACK
        // ========================================================

        backButton.addEventListener(
            "click",
            () => {

                clearDismissal();


                chrome.storage.local.set({
                    warningActive:
                        false
                });


                removeWarning();


                // ------------------------------------------------
                // Go back when possible.
                // ------------------------------------------------

                if (
                    window.history.length > 1
                ) {

                    window.history.back();

                }

                else {

                    // No usable history entry.
                    // Stay on the page rather than navigating
                    // to an arbitrary website.

                    window.location.replace(
                        "about:blank"
                    );

                }

            }
        );


        // ========================================================
        // CONTINUE ANYWAY
        // ========================================================

        continueButton.addEventListener(
            "click",
            () => {

                // ------------------------------------------------
                // Remember ONLY this exact page for this tab/session.
                //
                // This is NOT a whitelist.
                // The domain is not trusted permanently.
                // ------------------------------------------------

                dismissWarningForCurrentPage();


                chrome.storage.local.set({
                    warningActive:
                        false
                });


                removeWarning();

            }
        );


        buttons.appendChild(
            backButton
        );


        buttons.appendChild(
            continueButton
        );


        // ========================================================
        // FOOTER
        // ========================================================

        const footer =
            document.createElement(
                "div"
            );


        footer.className =
            "warning-footer";


        footer.textContent =
            "Phishing Detection AI • Multi-model security analysis";


        // ========================================================
        // BUILD CARD
        // ========================================================

        card.appendChild(
            icon
        );


        card.appendChild(
            title
        );


        card.appendChild(
            subtitle
        );


        card.appendChild(
            riskBox
        );


        card.appendChild(
            reasonsSection
        );


        card.appendChild(
            action
        );


        card.appendChild(
            buttons
        );


        card.appendChild(
            footer
        );


        overlay.appendChild(
            card
        );


        shadow.appendChild(
            overlay
        );


        // ========================================================
        // ADD TO PAGE
        // ========================================================

        function insertWarning() {

            if (
                !document.documentElement
            ) {

                return;

            }


            if (
                document.getElementById(
                    HOST_ID
                )
            ) {

                return;

            }


            document.documentElement.appendChild(
                host
            );

        }


        if (
            document.documentElement
        ) {

            insertWarning();

        }

        else {

            document.addEventListener(
                "DOMContentLoaded",
                insertWarning,
                {
                    once:
                        true
                }
            );

        }

    }


    // ============================================================
    // FORMAT PERCENTAGE
    // ============================================================

    function formatPercentage(
        value,
        fallbackScore
    ) {

        const number =
            Number(
                value
            );


        if (
            Number.isFinite(
                number
            )
        ) {

            return number.toFixed(
                2
            );

        }


        return (
            fallbackScore *
            100
        ).toFixed(
            2
        );

    }


    // ============================================================
    // REMOVE WARNING
    // ============================================================

    function removeWarning() {

        const existing =
            document.getElementById(
                HOST_ID
            );


        if (
            existing
        ) {

            existing.remove();

        }

    }


})();