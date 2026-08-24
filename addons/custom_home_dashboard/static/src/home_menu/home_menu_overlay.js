/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { CustomHomeDashboard } from "../dashboard/dashboard";

export class HomeMenuOverlay extends Component {
    static template = "custom_home_dashboard.HomeMenuOverlay";
    static components = { CustomHomeDashboard };
    static props = {};

    setup() {
        this.homeMenu = useService("home_menu");
        this.hm = useState(this.homeMenu.state);
    }
}

registry.category("main_components").add("custom_home_dashboard.HomeMenuOverlay", {
    Component: HomeMenuOverlay,
});
