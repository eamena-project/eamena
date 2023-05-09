define([
    'knockout',
    'viewmodels/card-component'
], function(ko, CardComponentViewModel) {

    var viewModel = function(params) {
        var self = this;

        this.state = params.state || 'form';
        this.preview = params.preview;
        this.loading = params.loading || ko.observable(false);
        this.provisionalTileViewModel = params.provisionalTileViewModel;

        this.card = params.card;
        this.form = params.form;
        this.expanded = ko.observable(true);
        this.values = ko.observableArray();
        this.uimapping = [];

        // We check for the addableCards method here because it only exists in resource edit mode.
        // If we let the following for loop run unchecked while in (for example) card designer mode,
        // this function will stop mid-way through, causing all sorts of horrible HTML errors during
        // rendering.
        if(this.form && (this.state === 'form') && this.form.addableCards)
        {
            // This loop simply fills the 'values' array with enough observable values for the number
            // of widgets we're going to render.
            var k = 0;
            for(i = 0; i <= this.card.cards().length; i++)
            {
                var card = this.card.cards()[i];
                if(card)
                {
                    self.uimapping[i] = [];
                    var c = card.widgets().length;
                    for(j = 0; j < c; j++)
                    {
                        self.values.push(ko.observable(""));
                        self.uimapping[i][j] = k;
                        k++;
                    }
                }
            }
        }

        // Ths purpose of the mapValue function is to assign a single numerical value for an
        // element in an observableArray, based on the tile (i) and widget (j) displayed on
        // the card. Each widget (of which there may be one or many per tile) needs its own
        // observable value, but we don't know at HTML render time how many widgets the
        // previous tile had, and therefore we can't keep track of our array index. Things
        // would be simpler if we could do 2D arrays in KnockOut, but I've not figured out
        // how to do that. So this function, local to this class, which of course knows how
        // many widgets each tile needs, is used to keep track of the array index, so we
        // can have multiple values per tile.
        this.mapValue = function(i, j)
        {
            return(self.uimapping[i][j]);
        }

        this.saveValue = function(arg)
        {
            var index = arg();
            var valueindex = self.uimapping[index];
            var savevalues = []
            var atile = this.card.tiles()[0];

            for(i = 0; i < valueindex.length; i++)
            {
                savevalues[i] = this.values()[valueindex[i]]();
            }

            // At this point, if atile is undefined, we need to create it. There is almost certainly a more
            // efficient way of doing this, but this works well for now.
            if(atile == null)
            {
                // This code block runs if there are no nodes created
                var topcard = this.card; // Explicitly set this here so the callback can access it
                self.tile.save(null, function(tileData) {

                    var newcard = topcard.tiles()[0].cards[index];
                    var newtile = newcard.getNewTile();
                    var keys = Object.keys(newtile.data);
                    var value_id = 0;
                    var savevalue = savevalues[value_id];
                    for(i = 0; i < keys.length; i++)
                    {
                        if(keys[i].startsWith('_')) { continue; }
                        if(typeof newtile.data[keys[i]] === "function")
                        {
                            newtile.data[keys[i]](savevalue); // If this is an observable already, it'll be a function
                            value_id++;
                            savevalue = savevalues[value_id];
                        } else {
                            newtile.data[keys[i]] = savevalue; // It's not an observable, so just set it.
                            value_id++;
                            savevalue = savevalues[value_id];
                        }
                    }
                    newtile.save(null, function(created){ newcard.parent.selected(true); });
		});
            } else {
                // This code block runs if there is a node, and we are just adding a value to it
                var newcard = this.card.tiles()[0].cards[index];
                var newtile = newcard.getNewTile();
                var keys = Object.keys(newtile.data);
                var value_id = 0;
                var savevalue = savevalues[value_id];
                for(i = 0; i < keys.length; i++)
                {
                    if(keys[i].startsWith('_')) { continue; }
                    if(typeof newtile.data[keys[i]] === "function")
                    {
                        newtile.data[keys[i]](savevalue); // If this is an observable already, it'll be a function
                        value_id++;
                        savevalue = savevalues[value_id];
                    } else {
                        newtile.data[keys[i]] = savevalue; // It's not an observable, so just set it.
                        value_id++;
                        savevalue = savevalues[value_id];
                    }
                }

                newtile.save(null, function(created){ newcard.parent.selected(true); });
            }
        };

        params.configKeys = ['selectSource', 'selectSourceLayer'];

        CardComponentViewModel.apply(this, [params]);
    };
    return ko.components.register('eamena-default-card', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/eamena-default-card.htm'
        }
    });
});
