/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { useEffect, useService } from "@web/core/utils/hooks";

const { Component } = owl;

//const companyMenuRegistry = registry.category("company_menuitems");

class CompanyMenuItem extends DropdownItem {
    setup() {
        super.setup();
        useEffect(
            () => {
                if (this.props.payload.id) {
                    this.el.dataset.menu = this.props.payload.id;
                }
            },
            () => []
        );
    }
}

export class CompanyMenu extends Component {
    setup() {

        const { origin } = browser.location;

        this.companyService = useService("company");
        const { companyId } = this.companyService.currentCompany;
        this.source = `${origin}/web/image?model=res.company&field=logo&id=1`;
    }
}
CompanyMenu.template = "web_company_logo.CompanyMenu";
CompanyMenu.components = { CompanyMenuItem };

export const systrayItem = {
    Component: CompanyMenu,
};
registry.category("systray").add("web_company_logo.company_menu", systrayItem, { sequence: 0 });
