define([
    'knockout',
    'arches',
    'js-cookie',
    'templates/views/components/plugins/curator.htm'
], function(ko, arches, Cookies, CuratorTemplate) {

    const CuratorViewModel = function() {
        const self = this;
        this.loading = ko.observable(true);
        this.datasets = ko.observable();

        this.getStatus = async function() {
            const response = await fetch("/curator");
            const data = await response.json();
            self.datasets(data.datasets);
            self.loading(false);
        };

        this.saveStatus = async function() {
            const response = await fetch("/curator", {
                method: 'POST',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                }
            });
            const data = await response.json();
            self.datasets(data.datasets);
        };

        this.uploadZenodo = function(){
                console.log("Zenodo upload.");
        };

        this.getStatus();
    };

    return ko.components.register('curator', {
        viewModel: CuratorViewModel,
        template: CuratorTemplate
    });
});
