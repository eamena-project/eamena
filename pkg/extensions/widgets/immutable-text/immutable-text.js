define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * registers an immutable-text-widget component for use in forms
    * @function external:"ko.components".immutable-text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    * @param {string} params.config().disabled - disables widget by default
    */
    return ko.components.register('immutable-text-widget', {
        viewModel: function(params) {
            params.configKeys = ['placeholder', 'width', 'maxLength', 'defaultValue', 'disabled'];
            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/immutable-text' }
    });
});

