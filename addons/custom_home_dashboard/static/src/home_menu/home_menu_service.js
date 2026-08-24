/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

export const homeMenuService = {
    dependencies: ["title"],
    start(env, { title }) {
        const state = reactive({ hasHomeMenu: false });
        let savedActionTitle = null;

        return {
            state,
            get hasHomeMenu() {
                return state.hasHomeMenu;
            },
            toggle(show) {
                const next = show === undefined ? !state.hasHomeMenu : show;
                if (next === state.hasHomeMenu) {
                    return;
                }
                state.hasHomeMenu = next;
                if (next) {
                    savedActionTitle = title.getParts().action;
                    title.setParts({ action: "Home" });
                } else {
                    title.setParts({ action: savedActionTitle });
                    savedActionTitle = null;
                }
            },
        };
    },
};

registry.category("services").add("home_menu", homeMenuService);
