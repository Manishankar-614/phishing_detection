const DEFAULT_REMOTE_API =
    "https://alternatively-roommates-recall-sur.trycloudflare.com/api";
const LOCAL_API =
    "http://127.0.0.1:5000/api";

async function getApiBaseUrl() {
    try {
        const stored = await chrome.storage.local.get("custom_api_url");
        if (stored && stored.custom_api_url && typeof stored.custom_api_url === "string" && stored.custom_api_url.trim()) {
            return stored.custom_api_url.trim().replace(/\/+$/, "");
        }
    } catch (e) {}
    return DEFAULT_REMOTE_API;
}


// ============================================================
// BEHAVIOR STATE PER TAB
// ============================================================

const tabBehavior =
    new Map();


const tabStartTimes =
    new Map();


// ============================================================
// DEFAULT BEHAVIOR
// ============================================================

function createDefaultBehavior() {

    return {

        num_clicks:
            0,

        time_on_page:
            0,

        num_redirects:
            0,

        failed_logins:
            0,

        mouse_speed:
            0,

        typing_speed:
            0,

        tab_switches:
            0

    };

}


// ============================================================
// GET TAB BEHAVIOR
// ============================================================

function getTabBehavior(
    tabId
) {

    if (
        !tabBehavior.has(
            tabId
        )
    ) {

        tabBehavior.set(

            tabId,

            createDefaultBehavior()

        );

    }


    return tabBehavior.get(
        tabId
    );

}


// ============================================================
// PAGE NAVIGATION
// ============================================================

chrome.webNavigation.onCommitted.addListener(

    (details) => {

        if (
            details.frameId !== 0
        ) {

            return;

        }


        const existing =
            getTabBehavior(
                details.tabId
            );


        tabBehavior.set(

            details.tabId,

            {

                ...createDefaultBehavior(),

                num_redirects:
                    (
                        existing.num_redirects
                        +
                        1
                    )

            }

        );


        tabStartTimes.set(

            details.tabId,

            Date.now()

        );


        console.log(
            "Navigation detected:",
            details.url
        );

    }

);


// ============================================================
// TAB SWITCH
// ============================================================

chrome.tabs.onActivated.addListener(

    (activeInfo) => {

        const behavior =
            getTabBehavior(
                activeInfo.tabId
            );


        behavior.tab_switches += 1;

    }

);


// ============================================================
// TAB CLOSED
// ============================================================

chrome.tabs.onRemoved.addListener(

    (tabId) => {

        tabBehavior.delete(
            tabId
        );


        tabStartTimes.delete(
            tabId
        );

    }

);


// ============================================================
// CONTENT SCRIPT MESSAGES
// ============================================================

chrome.runtime.onMessage.addListener(

    (
        message,
        sender,
        sendResponse
    ) => {

        const tabId =
            sender?.tab?.id;


        // ====================================================
        // BEHAVIOR UPDATE
        // ====================================================

        if (
            message.type ===
            "BEHAVIOR_UPDATE"
        ) {

            if (
                tabId === undefined
            ) {

                sendResponse({

                    success:
                        false

                });

                return true;

            }


            const behavior =
                getTabBehavior(
                    tabId
                );


            Object.assign(

                behavior,

                message.data || {}

            );


            sendResponse({

                success:
                    true

            });


            return true;

        }


        // ====================================================
        // GET BEHAVIOR
        // ====================================================

        if (
            message.type ===
            "GET_BEHAVIOR"
        ) {

            sendResponse({

                success:
                    true,

                behavior:
                    getBehaviorForTab(
                        tabId
                    )

            });


            return true;

        }


        // ====================================================
        // AUTO ANALYSIS
        // ====================================================

        if (
            message.type ===
            "AUTO_ANALYZE"
        ) {

            analyzePage(
                message.data
            )

            .then(

                (result) => {

                    sendResponse({

                        success:
                            true,

                        result

                    });

                }

            )

            .catch(

                (error) => {

                    console.error(
                        "Automatic analysis error:",
                        error
                    );


                    sendResponse({

                        success:
                            false,

                        error:
                            error.message

                    });

                }

            );


            return true;

        }


        // ====================================================
        // MANUAL ANALYSIS
        // ====================================================

        if (
            message.type ===
            "ANALYZE"
        ) {

            analyzePage(
                message.data
            )

            .then(

                (result) => {

                    sendResponse({

                        success:
                            true,

                        result

                    });

                }

            )

            .catch(

                (error) => {

                    console.error(
                        "Analysis error:",
                        error
                    );


                    sendResponse({

                        success:
                            false,

                        error:
                            error.message

                    });

                }

            );


            return true;

        }

    }

);


// ============================================================
// GET BEHAVIOR FOR TAB
// ============================================================

function getBehaviorForTab(
    tabId
) {

    if (
        tabId === undefined
    ) {

        return createDefaultBehavior();

    }


    const behavior =
        getTabBehavior(
            tabId
        );


    const startTime =
        tabStartTimes.get(
            tabId
        ) || Date.now();


    const elapsed =
        (
            Date.now() -
            startTime
        ) / 1000;


    return {

        num_clicks:
            Number(
                behavior.num_clicks
            ) || 0,

        time_on_page:
            Number(
                elapsed.toFixed(2)
            ),

        num_redirects:
            Number(
                behavior.num_redirects
            ) || 0,

        failed_logins:
            Number(
                behavior.failed_logins
            ) || 0,

        mouse_speed:
            Number(
                behavior.mouse_speed
            ) || 0,

        typing_speed:
            Number(
                behavior.typing_speed
            ) || 0,

        tab_switches:
            Number(
                behavior.tab_switches
            ) || 0

    };

}


// ============================================================
// ANALYZE PAGE
// ============================================================

async function analyzePage(
    data
) {

    const input =
        data || {};


    const isEmailPage =
        Boolean(
            input.is_email_page
        );


    const behavior =
        input.behavior || {};


    const pageUrl =
        typeof input.page_url ===
        "string"

            ? input.page_url

            :

            (
                typeof input.url ===
                "string"

                    ? input.url

                    : ""
            );


    const emailText =
        isEmailPage

            ? (
                typeof input.email ===
                "string"

                    ? input.email

                    : ""
            )

            : "";


    const emailUrls =
        Array.isArray(
            input.email_urls
        )

            ? input.email_urls

            : [];


    const emailLinks =
        Array.isArray(
            input.email_links
        )

            ? input.email_links

            : [];


    // ========================================================
    // BUILD API PAYLOAD
    // ========================================================

    const payload = {

        email:
            emailText,

        url:
            pageUrl,

        page_url:
            pageUrl,

        title:
            input.title || "",

        is_email_page:
            isEmailPage,

        email_urls:
            emailUrls,

        email_links:
            emailLinks,

        behavior: {

            num_clicks:
                Number(
                    behavior.num_clicks
                ) || 0,

            time_on_page:
                Number(
                    behavior.time_on_page
                ) || 0,

            num_redirects:
                Number(
                    behavior.num_redirects
                ) || 0,

            failed_logins:
                Number(
                    behavior.failed_logins
                ) || 0,

            mouse_speed:
                Number(
                    behavior.mouse_speed
                ) || 0,

            typing_speed:
                Number(
                    behavior.typing_speed
                ) || 0,

            tab_switches:
                Number(
                    behavior.tab_switches
                ) || 0

        }

    };


    // ========================================================
    // VALIDATE
    // ========================================================

    if (
        isEmailPage
    ) {

        if (
            !emailText.trim()
        ) {

            throw new Error(
                "No email content was detected."
            );

        }

    }

    else {

        if (
            !pageUrl
        ) {

            throw new Error(
                "Page URL is missing."
            );

        }

    }


    console.log(
        "Analysis payload:",
        payload
    );


    // ========================================================
    // SEND TO FLASK
    // ========================================================

    let response;
    const baseApi = await getApiBaseUrl();

    try {
        response = await fetch(
            `${baseApi}/analyze`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );
    } catch (error) {
        if (baseApi !== LOCAL_API) {
            console.warn("Primary API endpoint unreachable, attempting fallback to local API...");
            try {
                response = await fetch(
                    `${LOCAL_API}/analyze`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        },
                        body: JSON.stringify(payload)
                    }
                );
            } catch (fallbackError) {
                throw new Error("Unable to connect to PhishGuard AI API (cloud and local both unreachable). Please ensure the backend server or tunnel is running.");
            }
        } else {
            throw new Error("Unable to connect to Flask API. " + error.message);
        }
    }

    }


    // ========================================================
    // READ RESPONSE
    // ========================================================

    const responseText =
        await response.text();


    let result;


    try {

        result =
            responseText

                ? JSON.parse(
                    responseText
                )

                : {};

    }

    catch {

        result = {

            raw_response:
                responseText

        };

    }


    // ========================================================
    // API ERROR
    // ========================================================

    if (
        !response.ok
    ) {

        const message =
            result?.message ||
            result?.error ||
            responseText ||
            "Unknown API error.";


        throw new Error(

            `API request failed: ${response.status} - ${message}`

        );

    }


    // ========================================================
    // SAVE LATEST RESULT
    // ========================================================

    await chrome.storage.local.set({

        latestPhishingResult:
            result,

        latestAnalyzedUrl:
            pageUrl,

        latestAnalysisTime:
            Date.now(),

        latestAnalysisType:
            isEmailPage
                ? "email"
                : "website"

    });


    console.log(
        "Analysis result:",
        result
    );


    return result;

}