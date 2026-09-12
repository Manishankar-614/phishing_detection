console.log(
    "Phishing Detection AI content script loaded"
);


// ============================================================
// CONFIGURATION
// ============================================================

const PHISHING_WARNING_THRESHOLD = 0.70;

const AUTOMATIC_BANNER_ID =
    "phishing-detection-ai-banner";


// ============================================================
// BEHAVIOR STATE
// ============================================================

let clicks = 0;

let mouseDistances = [];

let mouseTimes = [];

let typingSpeeds = [];

let lastMouseX = null;

let lastMouseY = null;

let lastMouseTime = null;

let lastKeyTime = null;


// ============================================================
// AUTOMATIC ANALYSIS STATE
// ============================================================

let lastAnalysisFingerprint = "";

let lastAnalysisAttempt = 0;

let automaticAnalysisTimer = null;

let automaticBanner = null;


// ============================================================
// CLICK TRACKING
// ============================================================

document.addEventListener(
    "click",
    () => {

        clicks++;

        sendBehavior();

    },
    true
);


// ============================================================
// MOUSE TRACKING
// ============================================================

document.addEventListener(
    "mousemove",
    (event) => {

        const now =
            Date.now();


        if (
            lastMouseX !== null &&
            lastMouseY !== null &&
            lastMouseTime !== null
        ) {

            const dx =
                event.clientX -
                lastMouseX;


            const dy =
                event.clientY -
                lastMouseY;


            const distance =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );


            const elapsed =
                now -
                lastMouseTime;


            if (
                elapsed > 0 &&
                elapsed < 5000
            ) {

                mouseDistances.push(
                    distance
                );

                mouseTimes.push(
                    elapsed
                );


                if (
                    mouseDistances.length > 100
                ) {

                    mouseDistances.shift();

                }


                if (
                    mouseTimes.length > 100
                ) {

                    mouseTimes.shift();

                }

            }

        }


        lastMouseX =
            event.clientX;

        lastMouseY =
            event.clientY;

        lastMouseTime =
            now;

    },
    true
);


// ============================================================
// KEYBOARD TRACKING
// ============================================================

document.addEventListener(
    "keydown",
    () => {

        const now =
            Date.now();


        if (
            lastKeyTime !== null
        ) {

            const elapsed =
                now -
                lastKeyTime;


            if (
                elapsed > 0 &&
                elapsed < 5000
            ) {

                typingSpeeds.push(
                    1000 /
                    elapsed
                );


                if (
                    typingSpeeds.length > 100
                ) {

                    typingSpeeds.shift();

                }

            }

        }


        lastKeyTime =
            now;

    },
    true
);


// ============================================================
// MOUSE SPEED
// ============================================================

function calculateMouseSpeed() {

    if (
        mouseDistances.length === 0 ||
        mouseTimes.length === 0
    ) {

        return 0;

    }


    const totalDistance =
        mouseDistances.reduce(
            (
                sum,
                value
            ) =>
                sum + value,
            0
        );


    const totalTime =
        mouseTimes.reduce(
            (
                sum,
                value
            ) =>
                sum + value,
            0
        );


    if (
        totalTime === 0
    ) {

        return 0;

    }


    return (
        totalDistance /
        (
            totalTime /
            1000
        )
    );

}


// ============================================================
// TYPING SPEED
// ============================================================

function calculateTypingSpeed() {

    if (
        typingSpeeds.length === 0
    ) {

        return 0;

    }


    const total =
        typingSpeeds.reduce(
            (
                sum,
                value
            ) =>
                sum + value,
            0
        );


    return (
        total /
        typingSpeeds.length
    );

}


// ============================================================
// BEHAVIOR
// ============================================================

function getBehavior() {

    return {

        num_clicks:
            Number(clicks) || 0,

        time_on_page:
            0,

        num_redirects:
            0,

        failed_logins:
            0,

        mouse_speed:
            Number(
                calculateMouseSpeed()
                    .toFixed(2)
            ),

        typing_speed:
            Number(
                calculateTypingSpeed()
                    .toFixed(2)
            ),

        tab_switches:
            0

    };

}


// ============================================================
// SEND BEHAVIOR
// ============================================================

function sendBehavior() {

    try {

        chrome.runtime.sendMessage(
            {

                type:
                    "BEHAVIOR_UPDATE",

                data:
                    getBehavior()

            },

            () => {

                if (
                    chrome.runtime.lastError
                ) {

                    return;

                }

            }
        );

    }

    catch {

        return;

    }

}


// ============================================================
// EMAIL PROVIDER DETECTION
// ============================================================

function isEmailProvider(
    host
) {

    const providers = [

        "mail.google.com",

        "gmail.com",

        "outlook.live.com",

        "outlook.office.com",

        "outlook.com",

        "mail.yahoo.com",

        "mail.proton.me",

        "proton.me",

        "mail.aol.com",

        "icloud.com"

    ];


    return providers.some(
        (provider) =>

            host === provider ||

            host.endsWith(
                "." + provider
            )
    );

}


// ============================================================
// VISIBLE ELEMENT CHECK
// ============================================================

function isVisibleElement(
    element
) {

    if (!element) {

        return false;

    }


    const style =
        window.getComputedStyle(
            element
        );


    if (
        style.display ===
        "none"
    ) {

        return false;

    }


    if (
        style.visibility ===
        "hidden"
    ) {

        return false;

    }


    if (
        Number(
            style.opacity
        ) === 0
    ) {

        return false;

    }


    const rect =
        element.getBoundingClientRect();


    return (
        rect.width > 0 &&
        rect.height > 0
    );

}


// ============================================================
// GET EMAIL BODY ELEMENTS
// ============================================================

function getEmailBodyElements() {

    const selectors = [

        "div.a3s",

        "[aria-label='Message body']",

        "[aria-label='Message Body']",

        ".email-body",

        ".message-body",

        ".mail-body",

        "[data-message-body]",

        "[data-email-body]"

    ];


    const elements = [];


    selectors.forEach(
        (selector) => {

            const matches =
                document.querySelectorAll(
                    selector
                );


            matches.forEach(
                (element) => {

                    if (
                        !elements.includes(
                            element
                        )
                    ) {

                        elements.push(
                            element
                        );

                    }

                }
            );

        }
    );


    return elements;

}


// ============================================================
// GET CURRENT EMAIL BODY
// ============================================================

function getCurrentEmailBodyElement() {

    const elements =
        getEmailBodyElements();


    const visible =
        elements.filter(
            (element) =>
                isVisibleElement(
                    element
                )
        );


    if (
        visible.length === 0
    ) {

        return null;

    }


    const substantial =
        visible.filter(
            (element) => {

                const text =
                    (
                        element.innerText ||
                        ""
                    ).trim();


                return (
                    text.length > 20
                );

            }
        );


    if (
        substantial.length === 0
    ) {

        return visible[
            visible.length - 1
        ];

    }


    return substantial[
        substantial.length - 1
    ];

}


// ============================================================
// EXTRACT EMAIL CONTENT
// ============================================================

function extractEmailContent() {

    const element =
        getCurrentEmailBodyElement();


    if (!element) {

        return "";

    }


    let text =
        element.innerText ||
        "";


    text =
        text.replace(
            /\r/g,
            "\n"
        );


    const lines =
        text
            .split("\n")
            .map(
                (line) =>
                    line.trim()
            )
            .filter(
                (line) =>
                    line.length > 0
            );


    const cleaned = [];


    for (
        const line
        of lines
    ) {

        const lowered =
            line.toLowerCase();


        if (
            line.startsWith(
                ">"
            )
        ) {

            continue;

        }


        if (
            lowered.startsWith(
                "on "
            ) &&
            lowered.includes(
                " wrote:"
            )
        ) {

            break;

        }


        cleaned.push(
            line
        );

    }


    return cleaned
        .join(" ")
        .replace(
            /\s+/g,
            " "
        )
        .trim()
        .slice(
            0,
            12000
        );

}


// ============================================================
// PROCESS EMAIL LINK
// ============================================================

function processEmailLink(
    anchor,
    links
) {

    if (!anchor) {

        return;

    }


    const href =
        anchor.href;


    if (!href) {

        return;

    }


    if (
        !/^https?:\/\//i.test(
            href
        )
    ) {

        return;

    }


    let parsed;


    try {

        parsed =
            new URL(
                href
            );

    }

    catch {

        return;

    }


    const text = (

        anchor.innerText ||

        anchor.textContent ||

        ""

    )
        .replace(
            /\s+/g,
            " "
        )
        .trim()
        .slice(
            0,
            300
        );


    const exists =
        links.some(
            (item) =>
                item.url === href
        );


    if (
        !exists
    ) {

        links.push({

            url:
                href,

            text

        });

    }

}


// ============================================================
// EXTRACT EMAIL LINKS
// ============================================================

function extractEmailLinks() {

    const links = [];


    const body =
        getCurrentEmailBodyElement();


    if (!body) {

        return links;

    }


    const anchors =
        body.querySelectorAll(
            "a[href]"
        );


    anchors.forEach(
        (anchor) => {

            processEmailLink(
                anchor,
                links
            );

        }
    );


    return links.slice(
        0,
        20
    );

}


// ============================================================
// PAGE DATA
// ============================================================

function extractPageData() {

    const bodyText =
        document.body
            ? document.body.innerText
            : "";


    const title =
        document.title ||
        "";


    const pageUrl =
        window.location.href;


    const host =
        window.location.hostname
            .toLowerCase();


    const emailProvider =
        isEmailProvider(
            host
        );


    let emailText =
        "";

    let emailLinks =
        [];

    let emailUrls =
        [];


    if (
        emailProvider
    ) {

        emailText =
            extractEmailContent();


        emailLinks =
            extractEmailLinks();


        emailUrls =
            emailLinks.map(
                (link) =>
                    link.url
            );

    }


    const cleanedPage =
        bodyText
            .replace(
                /\s+/g,
                " "
            )
            .trim()
            .slice(
                0,
                12000
            );


    return {

        url:
            pageUrl,

        page_url:
            pageUrl,

        title,

        page_text:
            cleanedPage,

        email:
            emailText,

        email_urls:
            emailUrls,

        email_links:
            emailLinks,

        is_email_page:
            emailProvider,

        behavior:
            getBehavior()

    };

}


// ============================================================
// ANALYSIS FINGERPRINT
// ============================================================

function createAnalysisFingerprint(
    pageData
) {

    return JSON.stringify({

        url:
            pageData.page_url,

        email:
            pageData.email,

        email_urls:
            pageData.email_urls

    });

}


// ============================================================
// FORMAT SCORE
// ============================================================

function formatScore(
    value
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(
            number
        )
    ) {

        return "N/A";

    }


    return (

        Math.max(
            0,
            Math.min(
                100,
                number * 100
            )
        )

        .toFixed(2)

        + "%"

    );

}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(
    value
) {

    return String(
        value ?? ""
    )

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ============================================================
// GET REASONS
// ============================================================

function getReasons(
    result
) {

    const reasons =
        result?.explanation?.reasons;


    if (
        !Array.isArray(
            reasons
        )
    ) {

        return [];

    }


    return reasons;

}


// ============================================================
// REMOVE AUTOMATIC ANALYSIS PANEL
// ============================================================

function removeAutomaticBanner() {

    if (
        automaticBanner
    ) {

        automaticBanner.remove();

        automaticBanner =
            null;

    }


    const existing =
        document.getElementById(
            AUTOMATIC_BANNER_ID
        );


    if (
        existing
    ) {

        existing.remove();

    }

}


// ============================================================
// DETERMINE WHETHER BLOCKING WARNING IS REQUIRED
// ============================================================

function requiresBlockingWarning(
    result
) {

    const risk =
        result?.risk ||
        {};


    const classification =
        String(
            risk?.classification ||
            ""
        ).toLowerCase();


    const riskPercentage =
        Number(
            risk?.risk_percentage ??
            NaN
        );


    const riskScore =
        Number(
            risk?.risk_score ??
            NaN
        );


    const fusionScore =
        Number(
            result?.fusion?.fused_score ??
            NaN
        );


    let normalizedRisk =
        0;


    if (
        Number.isFinite(
            riskPercentage
        )
    ) {

        normalizedRisk =
            riskPercentage > 1
                ? riskPercentage / 100
                : riskPercentage;

    }

    else if (
        Number.isFinite(
            riskScore
        )
    ) {

        normalizedRisk =
            riskScore > 1
                ? riskScore / 100
                : riskScore;

    }

    else if (
        Number.isFinite(
            fusionScore
        )
    ) {

        normalizedRisk =
            fusionScore > 1
                ? fusionScore / 100
                : fusionScore;

    }


    return (

        normalizedRisk >=
        PHISHING_WARNING_THRESHOLD

        ||

        classification ===
        "phishing"

        ||

        classification ===
        "suspicious"

    );

}


// ============================================================
// AUTOMATIC ANALYSIS REQUEST
// ============================================================

function requestAutomaticAnalysis() {

    const pageData =
        extractPageData();


    // --------------------------------------------------------
    // Do not analyze an empty Gmail/Outlook page.
    // --------------------------------------------------------

    if (
        pageData.is_email_page &&
        !pageData.email
    ) {

        return;

    }


    // --------------------------------------------------------
    // Website must have URL.
    // --------------------------------------------------------

    if (
        !pageData.page_url
    ) {

        return;

    }


    const fingerprint =
        createAnalysisFingerprint(
            pageData
        );


    // --------------------------------------------------------
    // Same content already analyzed.
    // --------------------------------------------------------

    if (
        fingerprint ===
        lastAnalysisFingerprint
    ) {

        return;

    }


    // --------------------------------------------------------
    // Prevent rapid repeated requests.
    // --------------------------------------------------------

    const now =
        Date.now();


    if (
        now -
        lastAnalysisAttempt
        <
        3000
    ) {

        return;

    }


    lastAnalysisAttempt =
        now;


    chrome.runtime.sendMessage(

        {

            type:
                "AUTO_ANALYZE",

            data:
                pageData

        },

        (response) => {

            if (
                chrome.runtime.lastError
            ) {

                return;

            }


            if (
                response &&
                response.success
            ) {

                lastAnalysisFingerprint =
                    fingerprint;


                showAutomaticResult(
                    response.result
                );

            }

        }

    );

}


// ============================================================
// SCHEDULE AUTOMATIC ANALYSIS
// ============================================================

function scheduleAutomaticAnalysis(
    delay = 1200
) {

    if (
        automaticAnalysisTimer
    ) {

        clearTimeout(
            automaticAnalysisTimer
        );

    }


    automaticAnalysisTimer =
        setTimeout(

            () => {

                requestAutomaticAnalysis();

            },

            delay

        );

}


// ============================================================
// AUTOMATIC RESULT PANEL
//
// IMPORTANT:
//
// HIGH RISK:
//     Do NOT create this panel.
//     warning.js handles the blocking warning.
//
// LOW RISK:
//     Show the compact analysis panel.
// ============================================================

function showAutomaticResult(
    response
) {

    const result =
        response?.result ||
        response;


    if (!result) {

        return;

    }


    // --------------------------------------------------------
    // CRITICAL FIX
    //
    // If the warning system should be active, completely
    // remove the analysis panel and DO NOT recreate it.
    // --------------------------------------------------------

    if (
        requiresBlockingWarning(
            result
        )
    ) {

        removeAutomaticBanner();

        return;

    }


    const risk =
        result.risk ||
        {};


    const modelResults =
        result.model_results ||
        {};


    const fusion =
        result.fusion ||
        {};


    const bert =
        Number(
            modelResults?.bert?.score ??
            result?.email?.email_score ??
            0
        );


    const cnn =
        Number(
            modelResults?.cnn?.score ??
            result?.url?.url_score ??
            0
        );


    const behavior =
        Number(
            modelResults?.isolation_forest?.score ??
            result?.behavior?.behavior_score ??
            0
        );


    const fusionScore =
        Number(
            fusion?.fused_score ??
            risk?.risk_score ??
            0
        );


    const classification =
        String(
            risk?.classification ||
            "legitimate"
        ).toLowerCase();


    const agreementObject =
        modelResults?.model_agreement ??
        fusion?.model_agreement ??
        risk?.model_agreement;


    let agreement =
        "UNKNOWN";


    if (
        typeof agreementObject ===
        "string"
    ) {

        agreement =
            agreementObject.toUpperCase();

    }

    else if (
        agreementObject &&
        typeof agreementObject ===
        "object"
    ) {

        agreement =
            String(
                agreementObject.agreement ||
                "unknown"
            ).toUpperCase();

    }


    const dominant =
        String(
            modelResults?.dominant_model ??
            fusion?.dominant_model ??
            risk?.dominant_model ??
            "unknown"
        );


    const riskPercentage =
        Number(
            risk?.risk_percentage ??
            fusionScore * 100
        );


    const confidence =
        Number(
            risk?.confidence_percentage ??
            0
        );


    // --------------------------------------------------------
    // REMOVE PREVIOUS PANEL
    // --------------------------------------------------------

    removeAutomaticBanner();


    // --------------------------------------------------------
    // PANEL
    // --------------------------------------------------------

    const banner =
        document.createElement(
            "div"
        );


    automaticBanner =
        banner;


    banner.id =
        AUTOMATIC_BANNER_ID;


    banner.style.position =
    "fixed";

banner.style.right =
    "20px";

banner.style.top =
    "20px";

banner.style.bottom =
    "auto";

banner.style.width =
    "360px";

banner.style.maxWidth =
    "calc(100vw - 40px)";

banner.style.maxHeight =
    "calc(100vh - 40px)";

banner.style.overflowY =
    "auto";

banner.style.zIndex =
    "2147483646";

    banner.style.fontFamily =
        "Arial, Helvetica, sans-serif";


    banner.style.color =
        "#e5e7eb";


    banner.style.background =
        "#07111f";


    banner.style.border =
        "1px solid #26384d";


    banner.style.borderRadius =
        "16px";


    banner.style.boxShadow =
        "0 20px 50px rgba(0,0,0,0.40)";


    banner.style.overflowX =
        "hidden";


    // ========================================================
    // PANEL HTML
    // ========================================================

    banner.innerHTML = `

        <div style="
            padding:14px 15px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            border-bottom:1px solid #1e3044;
            background:#0b1828;
        ">

            <div style="
                display:flex;
                align-items:center;
                gap:9px;
            ">

                <div style="
                    width:9px;
                    height:9px;
                    border-radius:50%;
                    background:#22c55e;
                    box-shadow:0 0 10px rgba(34,197,94,0.65);
                "></div>

                <strong style="
                    color:#f8fafc;
                    font-size:14px;
                    font-weight:700;
                ">
                    Security Analysis
                </strong>

            </div>


            <button
                id="phishing-ai-close"
                aria-label="Close"
                style="
                    width:28px;
                    height:28px;
                    border:none;
                    border-radius:50%;
                    background:#17263a;
                    color:#cbd5e1;
                    cursor:pointer;
                    font-size:18px;
                    line-height:28px;
                    padding:0;
                "
            >
                ×
            </button>

        </div>


        <div style="
            padding:14px 15px;
        ">


            <!-- STATUS -->

            <div style="
                padding:12px;
                border-radius:11px;
                background:#0d1b2b;
                border:1px solid #1d3147;
            ">

                <div style="
                    color:#64748b;
                    font-size:9px;
                    font-weight:700;
                    letter-spacing:0.8px;
                ">
                    WEBSITE STATUS
                </div>


                <div style="
                    margin-top:5px;
                    color:#22c55e;
                    font-size:17px;
                    font-weight:800;
                ">
                    ${escapeHtml(
                        classification
                            .toUpperCase()
                    )}
                </div>


                <div style="
                    margin-top:4px;
                    color:#94a3b8;
                    font-size:10px;
                    line-height:1.45;
                ">
                    No high-risk phishing warning was triggered.
                </div>

            </div>


            <!-- RISK -->

            <div style="
                margin-top:14px;
                display:flex;
                justify-content:space-between;
                align-items:end;
            ">

                <div>

                    <div style="
                        color:#64748b;
                        font-size:9px;
                        font-weight:700;
                        letter-spacing:0.8px;
                    ">
                        PHISHING RISK
                    </div>

                    <div style="
                        margin-top:3px;
                        color:#f8fafc;
                        font-size:24px;
                        font-weight:800;
                    ">
                        ${Math.max(
                            0,
                            Math.min(
                                100,
                                riskPercentage
                            )
                        ).toFixed(2)}%
                    </div>

                </div>


                <div style="
                    color:#22c55e;
                    font-size:10px;
                    font-weight:700;
                ">
                    LOW RISK
                </div>

            </div>


            <!-- RISK BAR -->

            <div style="
                height:5px;
                margin-top:7px;
                background:#17263a;
                border-radius:20px;
                overflow:hidden;
            ">

                <div style="
                    height:100%;
                    width:${Math.max(
                        0,
                        Math.min(
                            100,
                            riskPercentage
                        )
                    )}%;
                    background:#22c55e;
                    border-radius:20px;
                "></div>

            </div>


            <!-- MODEL RESULTS -->

            <div style="
                margin-top:15px;
                color:#64748b;
                font-size:9px;
                font-weight:700;
                letter-spacing:0.8px;
            ">
                AI MODEL SIGNALS
            </div>


            <div style="
                margin-top:7px;
                display:grid;
                grid-template-columns:repeat(3,1fr);
                gap:6px;
            ">


                <div style="
                    padding:9px 5px;
                    text-align:center;
                    border-radius:9px;
                    background:#0d1b2b;
                    border:1px solid #1d3147;
                ">

                    <div style="
                        color:#64748b;
                        font-size:8px;
                    ">
                        BERT
                    </div>

                    <strong style="
                        display:block;
                        margin-top:4px;
                        color:#e2e8f0;
                        font-size:10px;
                    ">
                        ${formatScore(
                            bert
                        )}
                    </strong>

                </div>


                <div style="
                    padding:9px 5px;
                    text-align:center;
                    border-radius:9px;
                    background:#0d1b2b;
                    border:1px solid #1d3147;
                ">

                    <div style="
                        color:#64748b;
                        font-size:8px;
                    ">
                        CNN · URL
                    </div>

                    <strong style="
                        display:block;
                        margin-top:4px;
                        color:#e2e8f0;
                        font-size:10px;
                    ">
                        ${formatScore(
                            cnn
                        )}
                    </strong>

                </div>


                <div style="
                    padding:9px 5px;
                    text-align:center;
                    border-radius:9px;
                    background:#0d1b2b;
                    border:1px solid #1d3147;
                ">

                    <div style="
                        color:#64748b;
                        font-size:8px;
                    ">
                        BEHAVIOR
                    </div>

                    <strong style="
                        display:block;
                        margin-top:4px;
                        color:#e2e8f0;
                        font-size:10px;
                    ">
                        ${formatScore(
                            behavior
                        )}
                    </strong>

                </div>

            </div>


            <!-- FUSION -->

            <div style="
                margin-top:7px;
                display:grid;
                grid-template-columns:repeat(3,1fr);
                gap:6px;
            ">


                <div style="
                    padding:9px;
                    border-radius:9px;
                    background:#0d1b2b;
                ">

                    <div style="
                        color:#64748b;
                        font-size:8px;
                    ">
                        FUSION
                    </div>

                    <strong style="
                        display:block;
                        margin-top:4px;
                        color:#e2e8f0;
                        font-size:10px;
                    ">
                        ${formatScore(
                            fusionScore
                        )}
                    </strong>

                </div>


                <div style="
                    padding:9px;
                    border-radius:9px;
                    background:#0d1b2b;
                ">

                    <div style="
                        color:#64748b;
                        font-size:8px;
                    ">
                        AGREEMENT
                    </div>

                    <strong style="
                        display:block;
                        margin-top:4px;
                        color:#e2e8f0;
                        font-size:10px;
                    ">
                        ${escapeHtml(
                            agreement
                        )}
                    </strong>

                </div>


                <div style="
                    padding:9px;
                    border-radius:9px;
                    background:#0d1b2b;
                ">

                    <div style="
                        color:#64748b;
                        font-size:8px;
                    ">
                        CONFIDENCE
                    </div>

                    <strong style="
                        display:block;
                        margin-top:4px;
                        color:#e2e8f0;
                        font-size:10px;
                    ">
                        ${confidence.toFixed(2)}%
                    </strong>

                </div>

            </div>


            <!-- DOMINANT SIGNAL -->

            <div style="
                margin-top:13px;
                padding:10px 11px;
                border-radius:9px;
                background:#0d1b2b;
                border:1px solid #1d3147;
                font-size:10px;
                color:#64748b;
            ">

                Dominant signal:

                <strong style="
                    color:#cbd5e1;
                ">
                    ${escapeHtml(
                        dominant
                    )}
                </strong>

            </div>


            <!-- FOOTER -->

            <div style="
                margin-top:11px;
                color:#475569;
                font-size:8px;
                line-height:1.45;
            ">
                Analysis uses BERT, CNN and Isolation Forest.
            </div>

        </div>

    `;


    document.documentElement.appendChild(
        banner
    );


    // ========================================================
    // CLOSE
    // ========================================================

    const closeButton =
        banner.querySelector(
            "#phishing-ai-close"
        );


    if (
        closeButton
    ) {

        closeButton.onclick =
            () => {

                removeAutomaticBanner();

            };

    }

}


// ============================================================
// MESSAGE HANDLER
// ============================================================

chrome.runtime.onMessage.addListener(

    (
        message,
        sender,
        sendResponse
    ) => {


        if (
            !message
        ) {

            return;

        }


        if (
            message.type ===
            "GET_BEHAVIOR"
        ) {

            sendResponse({

                success:
                    true,

                behavior:
                    getBehavior()

            });


            return true;

        }


        if (
            message.type ===
            "GET_PAGE_DATA"
        ) {

            sendResponse({

                success:
                    true,

                data:
                    extractPageData()

            });


            return true;

        }


        if (
            message.type ===
            "RESET_BEHAVIOR"
        ) {

            clicks = 0;

            mouseDistances = [];

            mouseTimes = [];

            typingSpeeds = [];

            lastMouseX = null;

            lastMouseY = null;

            lastMouseTime = null;

            lastKeyTime = null;


            sendResponse({

                success:
                    true

            });


            return true;

        }

    }

);


// ============================================================
// PERIODIC BEHAVIOR UPDATE
// ============================================================

setInterval(
    () => {

        sendBehavior();

    },
    3000
);


// ============================================================
// DYNAMIC PAGE MONITOR
// ============================================================

let lastObservedUrl =
    window.location.href;


let lastObservedFingerprint =
    "";


setInterval(
    () => {

        const currentUrl =
            window.location.href;


        const pageData =
            extractPageData();


        const fingerprint =
            createAnalysisFingerprint(
                pageData
            );


        if (
            currentUrl !==
            lastObservedUrl
        ) {

            lastObservedUrl =
                currentUrl;


            lastAnalysisFingerprint =
                "";


            removeAutomaticBanner();


            scheduleAutomaticAnalysis(
                1000
            );


            return;

        }


        if (
            fingerprint !==
            lastObservedFingerprint
        ) {

            lastObservedFingerprint =
                fingerprint;


            scheduleAutomaticAnalysis(
                1200
            );

        }

    },
    2000
);


// ============================================================
// INITIAL ANALYSIS
// ============================================================

function startAutomaticAnalysis() {

    setTimeout(
        () => {

            scheduleAutomaticAnalysis(
                500
            );

        },
        2500
    );

}


if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        () => {

            startAutomaticAnalysis();

        },
        {
            once:
                true
        }
    );

}

else {

    startAutomaticAnalysis();

}


// ============================================================
// INITIAL BEHAVIOR
// ============================================================

sendBehavior();