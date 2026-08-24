/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

export const homeMenuService = {
    start() {
        const state = reactive({ hasHomeMenu: false });
        return {
            state,
            get hasHomeMenu() {
                return state.hasHomeMenu;
            },
            toggle(show) {
                state.hasHomeMenu = show === undefined ? !state.hasHomeMenu : show;
            },
        };
    },
};

registry.category("services").add("home_menu", homeMenuService);
