/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, useRef, onMounted } from "@odoo/owl";

const SELF_XMLID = "custom_home_dashboard.menu_custom_home_dashboard_root";

export class CustomHomeDashboard extends Component {
    static template = "custom_home_dashboard.Dashboard";

    setup() {
        this.menuService = useService("menu");
        this.homeMenu = useService("home_menu");
        this.searchRef = useRef("search");
        this.state = useState({ query: "" });
        this.allApps = this.menuService.getApps().filter((app) => app.xmlid !== SELF_XMLID);
        onMounted(() => this.searchRef.el?.focus());
    }

    get apps() {
        const query = this.state.query.trim().toLowerCase();
        if (!query) {
            return this.allApps;
        }
        return this.allApps.filter((app) => app.name.toLowerCase().includes(query));
    }

    openApp(app) {
        this.menuService.selectMenu(app);
        this.homeMenu.toggle(false);
    }

    onTileKeydown(ev, app) {
        if (ev.key === "Enter") {
            this.openApp(app);
        }
    }

    onSearchInput(ev) {
        this.state.query = ev.target.value;
    }

    onSearchKeydown(ev) {
        if (ev.key === "Enter" && this.apps.length) {
            this.openApp(this.apps[0]);
        } else if (ev.key === "Escape") {
            this.state.query = "";
        }
    }
}

registry.category("actions").add("custom_home_dashboard.dashboard", CustomHomeDashboard);
