define(['knockout',
        'viewmodels/function',
        'bindings/select2-query'],
function (ko, FunctionViewModel, select2Query) {
    return ko.components.register('views/components/functions/incrementor-function', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            console.log(select2Query)
            var self = this;
            var nodegroups = {};
            this.rerender = ko.observable(true);
            this.cards = ko.observableArray();
            this.nodes = ko.observableArray([]);
            this.selected_nodegroup = params.config.selected_nodegroup;
            this.target_node = params.config.target_node;
            this.starting_value = params.config.starting_value;
            this.last_value = params.config.last_value;
            this.prefix = params.config.prefix;
            this.suffix = params.config.suffix;
            
            this.selected_nodegroup.subscribe(function(){
                self.rerender(false); //Toggling rerender forces the node options to load in the select2 dropdown when the card changes
                var nodes = self.graph.nodes.filter(function(node){
                    return node.nodegroup_id === self.selected_nodegroup();
                }).map(function(node){
                    node.id = node.nodeid;
                    node.text = node.name;
                    return node;
                });
                self.nodes.removeAll();
                self.nodes(nodes);
                self.rerender(true);
            });

            this.graph.cards.forEach(function(card){
                var found = !!_.find(this.graph.nodegroups, function(nodegroup){
                    return nodegroup.parentnodegroup_id === card.nodegroup_id
                }, this);
                if(!found && !(card.nodegroup_id in nodegroups)){
                    card.id = card.nodegroup_id;
                    card.text = card.name;
                    this.cards.push(card);
                    nodegroups[card.nodegroup_id] = true;
                }
            }, this);

            this.selected_nodegroup.valueHasMutated(); // Forces the node value to load into the node options when the template is rendered
            
        },
        template: {
            require: 'text!templates/views/components/functions/incrementor-function.htm'
        }
    });
})
