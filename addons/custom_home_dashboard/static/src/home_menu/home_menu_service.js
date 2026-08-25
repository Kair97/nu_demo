/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Mutex } from "@web/core/utils/concurrency";
import {
    ControllerNotFoundError,
    standardActionServiceProps,
} from "@web/webclient/actions/action_service";
import { CustomHomeDashboard } from "../dashboard/dashboard";
import { Component, onMounted, onWillUnmount, reactive, xml } from "@odoo/owl";

/**
 * The home menu is registered as a real client action under the tag "menu"
 * rather than being drawn as a floating overlay.
 *
 * That tag is not arbitrary: Odoo's router special-cases it (see stateToUrl in
 * web/core/browser/router.js) and renders a bare "/odoo" URL for it instead of
 * "/odoo/<action>". Going through the action service therefore gets correct URL
 * syncing, working refresh, and browser back/forward for free -- none of which
 * an overlay could provide, since an overlay never touches the router at all.
 */
export const homeMenuService = {
    dependencies: ["action"],
    start(env) {
        const state = reactive({ hasHomeMenu: false, toggle });
        const mutex = new Mutex(); // guards against double-clicking the toggle

        class HomeMenuAction extends Component {
            static components = { CustomHomeDashboard };
            static target = "current";
            static props = { ...standardActionServiceProps };
            static template = xml`<CustomHomeDashboard/>`;
            // The action service copies displayName into the browser tab title,
            // so this is also what makes the tab read "Home".
            static displayName = _t("Home");

            setup() {
                onMounted(() => {
                    state.hasHomeMenu = true;
                });
                onWillUnmount(() => {
                    state.hasHomeMenu = false;
                });
            }
        }

        registry.category("actions").add("menu", HomeMenuAction);

        async function toggle(show) {
            return mutex.exec(async () => {
                show = show === undefined ? !state.hasHomeMenu : Boolean(show);
                if (show !== state.hasHomeMenu) {
                    if (show) {
                        await env.services.action.doAction("menu");
                    } else {
                        try {
                            // Pops back to whatever was open underneath, restoring
                            // both the view and its URL.
                            await env.services.action.restore();
                        } catch (err) {
                            if (!(err instanceof ControllerNotFoundError)) {
                                throw err;
                            }
                        }
                    }
                }
                // Let the router finish writing the URL before another toggle runs.
                return new Promise((r) => setTimeout(r));
            });
        }

        return state;
    },
};

registry.category("services").add("home_menu", homeMenuService);
