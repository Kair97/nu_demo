/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";

patch(NavBar.prototype, {
    goToDashboard() {
        this.actionService.doAction("custom_home_dashboard.action_custom_home_dashboard", {
            clearBreadcrumbs: true,
        });
    },
});
