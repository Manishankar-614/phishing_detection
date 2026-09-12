const currentUrlElement =
    document.getElementById(
        "current-url"
    );

const analyzeButton =
    document.getElementById(
        "analyze-btn"
    );

const loading =
    document.getElementById(
        "loading"
    );

const errorElement =
    document.getElementById(
        "error"
    );

const analysisElement =
    document.getElementById(
        "analysis"
    );

const warningState =
    document.getElementById(
        "warning-state"
    );

const safeState =
    document.getElementById(
        "safe-state"
    );

const protectionDot =
    document.getElementById(
        "protection-dot"
    );


// ============================================================
// CURRENT TAB
// ============================================================

async function getCurrentTab() {

    const tabs =
        await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

    return tabs[0];
}


// ============================================================
// INITIALIZE
// ============================================================

async function initialize() {

    try {

        const tab =
            await getCurrentTab();


        if (
            !tab ||
            !tab.url
        ) {

            currentUrlElement.textContent =
                "Unable to detect URL";

            return;
        }


        currentUrlElement.textContent =
            tab.url;


        const stored =
            await chrome.storage.local.get([
                "latestPhishingResult",
                "latestAnalyzedUrl",
                "warningActive"
            ]);


        // --------------------------------------------------------
        // WARNING ACTIVE
        // --------------------------------------------------------

        if (
            stored.warningActive === true &&
            stored.latestAnalyzedUrl === tab.url
        ) {

            showWarningState();

            return;
        }


        // --------------------------------------------------------
        // NORMAL STATE
        // --------------------------------------------------------

        showSafeState();


        // --------------------------------------------------------
        // SHOW ANALYSIS ONLY WHEN THERE IS NO WARNING
        // --------------------------------------------------------

        if (
            stored.latestPhishingResult &&
            stored.latestAnalyzedUrl === tab.url
        ) {

            displayResult(
                stored.latestPhishingResult
            );
        }

    }
    catch (error) {

        console.error(
            error
        );

        currentUrlElement.textContent =
            "Unable to detect URL";
    }
}


// ============================================================
// WARNING STATE
// ============================================================

function showWarningState() {

    warningState.classList.remove(
        "hidden"
    );

    safeState.classList.add(
        "hidden"
    );

    analysisElement.classList.add(
        "hidden"
    );

    protectionDot.style.background =
        "#ef4444";

    protectionDot.style.boxShadow =
        "0 0 10px rgba(239,68,68,0.7)";

    analyzeButton.disabled =
        true;

    analyzeButton.textContent =
        "Warning Active";
}


// ============================================================
// SAFE STATE
// ============================================================

function showSafeState() {

    warningState.classList.add(
        "hidden"
    );

    safeState.classList.remove(
        "hidden"
    );

    protectionDot.style.background =
        "#22c55e";

    protectionDot.style.boxShadow =
        "0 0 10px rgba(34,197,94,0.7)";

    analyzeButton.disabled =
        false;

    analyzeButton.textContent =
        "Analyze Current Website";
}


// ============================================================
// MANUAL ANALYZE
// ============================================================

analyzeButton.addEventListener(
    "click",
    async () => {

        hideError();


        analysisElement.classList.add(
            "hidden"
        );


        loading.classList.remove(
            "hidden"
        );


        analyzeButton.disabled =
            true;


        try {

            const tab =
                await getCurrentTab();


            if (
                !tab ||
                !tab.id ||
                !tab.url
            ) {

                throw new Error(
                    "Unable to access the current webpage."
                );
            }


            // ----------------------------------------------------
            // GET PAGE DATA
            // ----------------------------------------------------

            const pageData =
                await new Promise(
                    (
                        resolve,
                        reject
                    ) => {

                        chrome.tabs.sendMessage(
                            tab.id,
                            {
                                type:
                                    "GET_PAGE_DATA"
                            },
                            (response) => {

                                if (
                                    chrome.runtime.lastError
                                ) {

                                    reject(
                                        new Error(
                                            "Unable to communicate with the webpage. Refresh the page and try again."
                                        )
                                    );

                                    return;
                                }


                                if (
                                    !response ||
                                    !response.success
                                ) {

                                    reject(
                                        new Error(
                                            "Unable to collect webpage data."
                                        )
                                    );

                                    return;
                                }


                                resolve(
                                    response.data
                                );
                            }
                        );
                    }
                );


            // ----------------------------------------------------
            // ANALYZE
            // ----------------------------------------------------

            const response =
                await chrome.runtime.sendMessage({
                    type:
                        "ANALYZE",

                    data:
                        pageData
                });


            if (
                !response ||
                !response.success
            ) {

                throw new Error(
                    response?.error ||
                    "Analysis failed."
                );
            }


            // ----------------------------------------------------
            // CHECK WHETHER WARNING SHOULD BE ACTIVE
            // ----------------------------------------------------

            const result =
                response.result;


            const risk =
                result?.result?.risk ||
                result?.risk;


            const riskScore =
                Number(
                    risk?.risk_score
                );


            if (
                Number.isFinite(
                    riskScore
                ) &&
                riskScore >= 0.70
            ) {

                await chrome.storage.local.set({
                    warningActive:
                        true
                });


                showWarningState();


                /*
                 * The warning.js content script will display
                 * the blocking warning.
                 *
                 * Do NOT display the detailed popup analysis.
                 */

                return;
            }


            // ----------------------------------------------------
            // SAFE / NON-BLOCKING RESULT
            // ----------------------------------------------------

            await chrome.storage.local.set({
                warningActive:
                    false
            });


            showSafeState();


            displayResult(
                result
            );

        }
        catch (error) {

            console.error(
                error
            );

            showError(
                error.message
            );

        }
        finally {

            loading.classList.add(
                "hidden"
            );


            if (
                !warningState.classList.contains(
                    "hidden"
                )
            ) {

                analyzeButton.disabled =
                    true;

            }
            else {

                analyzeButton.disabled =
                    false;
            }
        }
    }
);


// ============================================================
// DISPLAY RESULT
// ============================================================

function displayResult(
    response
) {

    const result =
        response?.result ||
        response;


    if (
        !result ||
        !result.risk
    ) {

        return;
    }


    const risk =
        result.risk;

    const email =
        result.email ||
        {};

    const url =
        result.url ||
        {};

    const behavior =
        result.behavior ||
        {};

    const fusion =
        result.fusion ||
        {};

    const explanation =
        result.explanation ||
        {};


    // ----------------------------------------------------------
    // RISK
    // ----------------------------------------------------------

    const riskPercentage =
        Number(
            risk.risk_percentage ||
            0
        );


    document.getElementById(
        "risk-score"
    ).textContent =
        `${riskPercentage.toFixed(2)}%`;


    document.getElementById(
        "risk-bar"
    ).style.width =
        `${Math.min(
            100,
            riskPercentage
        )}%`;


    // ----------------------------------------------------------
    // CLASSIFICATION
    // ----------------------------------------------------------

    document.getElementById(
        "classification"
    ).textContent =
        (
            risk.classification ||
            "UNKNOWN"
        ).toUpperCase();


    // ----------------------------------------------------------
    // MODEL SCORES
    // ----------------------------------------------------------

    setModelScore(
        "email",
        Number(
            email.email_score
        ) || 0
    );


    setModelScore(
        "url",
        Number(
            url.url_score
        ) || 0
    );


    setModelScore(
        "behavior",
        Number(
            behavior.behavior_score
        ) || 0
    );


    // ----------------------------------------------------------
    // FUSION
    // ----------------------------------------------------------

    if (
        fusion.fused_score !==
        undefined
    ) {

        document.getElementById(
            "fusion-score"
        ).textContent =
            `${(
                Number(
                    fusion.fused_score
                ) *
                100
            ).toFixed(2)}%`;
    }


    // ----------------------------------------------------------
    // AGREEMENT
    // ----------------------------------------------------------

    if (
        fusion.model_agreement
    ) {

        document.getElementById(
            "agreement"
        ).textContent =
            (
                fusion
                    .model_agreement
                    .agreement ||
                "UNKNOWN"
            ).toUpperCase();
    }


    // ----------------------------------------------------------
    // CONFIDENCE
    // ----------------------------------------------------------

    if (
        risk.confidence_percentage !==
        undefined
    ) {

        document.getElementById(
            "confidence"
        ).textContent =
            `${Number(
                risk.confidence_percentage
            ).toFixed(2)}%`;
    }


    // ----------------------------------------------------------
    // EXPLANATION
    // ----------------------------------------------------------

    document.getElementById(
        "summary"
    ).textContent =
        explanation.summary ||
        "The analysis was completed using multiple security signals.";


    const reasons =
        document.getElementById(
            "reasons"
        );


    reasons.innerHTML =
        "";


    (
        explanation.reasons ||
        []
    )
        .slice(
            0,
            4
        )
        .forEach(
            (reason) => {

                const element =
                    document.createElement(
                        "div"
                    );


                element.className =
                    "reason";


                element.textContent =
                    typeof reason ===
                    "string"
                        ? reason
                        : (
                            reason?.reason ||
                            reason?.message ||
                            ""
                        );


                reasons.appendChild(
                    element
                );
            }
        );


    // ----------------------------------------------------------
    // SHOW
    // ----------------------------------------------------------

    analysisElement.classList.remove(
        "hidden"
    );
}


// ============================================================
// MODEL SCORE
// ============================================================

function setModelScore(
    model,
    score
) {

    const percentage =
        (
            Number(score) *
            100
        ).toFixed(2);


    const scoreElement =
        document.getElementById(
            `${model}-score`
        );


    if (
        scoreElement
    ) {

        scoreElement.textContent =
            `${percentage}%`;
    }
}


// ============================================================
// ERROR
// ============================================================

function showError(
    message
) {

    errorElement.textContent =
        message;

    errorElement.classList.remove(
        "hidden"
    );
}


// ============================================================
// HIDE ERROR
// ============================================================

function hideError() {

    errorElement.classList.add(
        "hidden"
    );
}


// ============================================================
// STORAGE CHANGES
// ============================================================

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
            changes.warningActive
        ) {

            if (
                changes.warningActive.newValue === true
            ) {

                showWarningState();

            }
            else {

                showSafeState();
            }
        }
    }
);


// ============================================================
// START
// ============================================================

initialize();