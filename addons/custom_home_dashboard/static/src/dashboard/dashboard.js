/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Component, useState, useRef, onMounted } from "@odoo/owl";

export class CustomHomeDashboard extends Component {
    static template = "custom_home_dashboard.Dashboard";
    static props = {};

    setup() {
        this.menuService = useService("menu");
        this.searchRef = useRef("search");
        this.state = useState({ query: "" });
        this.allApps = this.menuService.getApps();
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
        // selectMenu runs its own doAction, which unmounts the home-menu action
        // and flips hasHomeMenu back to false on its own -- no manual toggle.
        this.menuService.selectMenu(app);
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
