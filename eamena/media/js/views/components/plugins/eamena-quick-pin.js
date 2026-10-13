define([
    'knockout',
    'jquery',
    'arches',
    'mapbox-gl',
    'models/tile'
], function(ko, $, arches, mapboxgl, TileModel) {

    var QuickPinViewModel = function(params) {
        var self = this;

        // =====================================================
        // EAMENA / ARCHES CONFIGURATION
        // =====================================================

        self.heritagePlaceGraphId =
            '34cfe98e-c2c0-11ea-9026-02e7594ce0a0';

        self.spatialNodeId =
            '5348cf67-c2c5-11ea-9026-02e7594ce0a0';

        self.spatialNodeGroupId =
            '3080eebe-c2c5-11ea-9026-02e7594ce0a0';


        // =====================================================
        // DRAWING STATE
        // =====================================================

        self.marker = null;
        self.searchMarker = null;

        self.drawingMode = ko.observable('point');

        self.polygonPoints = ko.observableArray([]);

        self.cursorPoint = null;

        self.isPolygonClosed = ko.observable(false);


        // =====================================================
        // DRAGGING STATE
        // =====================================================

        self.isDraggingVertex = false;

        self.draggedVertexIndex = null;


        // =====================================================
        // SEARCH STATE
        // =====================================================

        self.geometrySearchQuery = ko.observable('');


        // =====================================================
        // MODAL / SAVE STATE
        // =====================================================

        self.showModal = ko.observable(false);

        self.currentFeature = ko.observable(null);

        self.featureType = ko.observable('');

        self.coordinateDisplay = ko.observable('');

        self.isSaving = ko.observable(false);

        self.saveSuccess = ko.observable(false);

        self.savedResourceId = ko.observable('');

        self.savedResourceUrl = ko.observable('');


        // =====================================================
        // UUID GENERATOR
        // =====================================================

        self.generateUUID = function() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
                .replace(/[xy]/g, function(c) {

                    var r = Math.random() * 16 | 0;

                    var v = c === 'x'
                        ? r
                        : (r & 0x3 | 0x8);

                    return v.toString(16);
                });
        };


        // =====================================================
        // INITIALISE MAP
        // =====================================================

        self.initMap = function() {

            mapboxgl.accessToken = arches.mapboxApiKey;


            self.map = new mapboxgl.Map({

                container: 'plugin-map-container',

                style: 'mapbox://styles/mapbox/satellite-v9',

                center: [25.0, 28.0],

                zoom: 5
            });


            // -------------------------------------------------
            // MAPBOX ERROR LOGGING
            // -------------------------------------------------

            self.map.on('error', function(e) {

                console.error(
                    'Quick Pin Mapbox error:',
                    e.error || e
                );

            });


            // -------------------------------------------------
            // MAP CONTROLS
            // -------------------------------------------------

            self.map.addControl(
                new mapboxgl.NavigationControl(),
                'top-right'
            );

            self.map.doubleClickZoom.disable();


            // =================================================
            // MAP LOADED
            // =================================================

            self.map.on('load', function() {


                // =============================================
                // 1. EXISTING EAMENA HERITAGE PLACES
                // =============================================

                var mvtUrl =
                    window.location.origin +
                    arches.urls.mvt(self.spatialNodeId);


                console.log(
                    'Quick Pin spatial node:',
                    self.spatialNodeId
                );

                console.log(
                    'Quick Pin MVT URL:',
                    mvtUrl
                );


                self.map.addSource(
                    'existing-heritage-places',
                    {

                        type: 'vector',

                        tiles: [
                            mvtUrl
                        ],

                        minzoom: 0,

                        maxzoom: 22
                    }
                );


                // ---------------------------------------------
                // EXISTING POLYGONS
                // ---------------------------------------------

                self.map.addLayer({

                    id: 'existing-places-fill',

                    type: 'fill',

                    source: 'existing-heritage-places',

                    'source-layer': self.spatialNodeId,

                    filter: [
                        '==',
                        '$type',
                        'Polygon'
                    ],

                    paint: {

                        'fill-color': '#7b61ef',

                        'fill-opacity': 0.3
                    }
                });


                // ---------------------------------------------
                // EXISTING POLYGON / LINE OUTLINES
                // ---------------------------------------------

                self.map.addLayer({

                    id: 'existing-places-line',

                    type: 'line',

                    source: 'existing-heritage-places',

                    'source-layer': self.spatialNodeId,

                    filter: [
                        '!=',
                        '$type',
                        'Point'
                    ],

                    paint: {

                        'line-color': '#ffaa00',

                        'line-width': 2
                    }
                });


                // ---------------------------------------------
                // EXISTING POINTS
                // ---------------------------------------------

                self.map.addLayer({

                    id: 'existing-places-point',

                    type: 'circle',

                    source: 'existing-heritage-places',

                    'source-layer': self.spatialNodeId,

                    filter: [
                        '==',
                        '$type',
                        'Point'
                    ],

                    paint: {

                        'circle-color': '#ffaa00',

                        'circle-radius': [
                            'case',
                            ['has', 'point_count'],
                            12,
                            5
                        ],

                        'circle-stroke-width': 1,

                        'circle-stroke-color': '#ffffff'
                    }
                });


                // =============================================
                // 2. CUSTOM DRAWING SOURCE
                // =============================================

                self.map.addSource(
                    'draw-source',
                    {

                        type: 'geojson',

                        data: {

                            type: 'FeatureCollection',

                            features: []
                        }
                    }
                );


                // ---------------------------------------------
                // DRAW POLYGON FILL
                // ---------------------------------------------

                self.map.addLayer({

                    id: 'draw-fill',

                    type: 'fill',

                    source: 'draw-source',

                    filter: [
                        '==',
                        ['geometry-type'],
                        'Polygon'
                    ],

                    paint: {

                        'fill-color': '#007bff',

                        'fill-opacity': 0.3
                    }
                });


                // ---------------------------------------------
                // DRAW POLYGON OUTLINE
                // ---------------------------------------------

                self.map.addLayer({

                    id: 'draw-outline',

                    type: 'line',

                    source: 'draw-source',

                    filter: [
                        'match',
                        ['geometry-type'],
                        [
                            'Polygon',
                            'LineString'
                        ],
                        true,
                        false
                    ],

                    paint: {

                        'line-color': '#007bff',

                        'line-width': 2
                    }
                });


                // ---------------------------------------------
                // DRAW VERTICES
                // ---------------------------------------------

                self.map.addLayer({

                    id: 'draw-vertices',

                    type: 'circle',

                    source: 'draw-source',

                    filter: [
                        '==',
                        ['geometry-type'],
                        'Point'
                    ],

                    paint: {

                        'circle-color': [
                            'case',

                            [
                                'boolean',
                                ['feature-state', 'isFirst'],
                                false
                            ],

                            '#28a745',

                            '#ff0000'
                        ],

                        'circle-radius': [
                            'case',

                            [
                                'boolean',
                                ['feature-state', 'isFirst'],
                                false
                            ],

                            7,

                            5
                        ],

                        'circle-stroke-color': '#ffffff',

                        'circle-stroke-width': 2
                    }
                });


                // =============================================
                // 3. SEARCH GEOMETRY HIGHLIGHT
                // =============================================

                self.map.addSource(
                    'search-highlight-source',
                    {

                        type: 'geojson',

                        data: {

                            type: 'FeatureCollection',

                            features: []
                        }
                    }
                );


                self.map.addLayer({

                    id: 'search-highlight-fill',

                    type: 'fill',

                    source: 'search-highlight-source',

                    filter: [
                        '==',
                        ['geometry-type'],
                        'Polygon'
                    ],

                    paint: {

                        'fill-color': '#ffff00',

                        'fill-opacity': 0.4
                    }
                });


                self.map.addLayer({

                    id: 'search-highlight-outline',

                    type: 'line',

                    source: 'search-highlight-source',

                    paint: {

                        'line-color': '#ffea00',

                        'line-width': 3
                    }
                });


                // =============================================
                // INITIAL ZOOM TO EXISTING EAMENA DATA
                // =============================================

                var eamenaBounds = [

                    [-18.0, 10.0 ],
                    [64.0, 42.0]

                ];


                self.map.fitBounds(
                    eamenaBounds,
                    {

                        padding: 45,

                        maxZoom: 17,

                        duration: 0
                    }
                );

            });


            // =================================================
            // VERTEX EDITING ENGINE
            // =================================================

            self.map.on(
                'mouseenter',
                'draw-vertices',
                function() {

                    if (self.isPolygonClosed()) {

                        self.map
                            .getCanvas()
                            .style
                            .cursor = 'grab';
                    }

                }
            );


            self.map.on(
                'mouseleave',
                'draw-vertices',
                function() {

                    if (!self.isDraggingVertex) {

                        self.map
                            .getCanvas()
                            .style
                            .cursor = '';
                    }

                }
            );


            self.map.on(
                'mousedown',
                'draw-vertices',
                function(e) {

                    if (!self.isPolygonClosed()) {
                        return;
                    }

                    e.preventDefault();

                    self.map.dragPan.disable();

                    self.isDraggingVertex = true;

                    self.map
                        .getCanvas()
                        .style
                        .cursor = 'grabbing';


                    var features =
                        self.map.queryRenderedFeatures(
                            e.point,
                            {
                                layers: [
                                    'draw-vertices'
                                ]
                            }
                        );


                    if (features.length > 0) {

                        self.draggedVertexIndex =
                            features[0].id;
                    }

                }
            );


            self.map.on(
                'mousemove',
                function(e) {

                    if (
                        self.isDraggingVertex &&
                        self.draggedVertexIndex !== null
                    ) {

                        var pts =
                            self.polygonPoints();


                        pts[
                            self.draggedVertexIndex
                        ] = [
                            e.lngLat.lng,
                            e.lngLat.lat
                        ];


                        self.polygonPoints(pts);

                        self.updateDrawLayer();

                    }

                    else if (
                        self.drawingMode() === 'polygon' &&
                        self.polygonPoints().length > 0 &&
                        !self.isPolygonClosed() &&
                        !self.showModal()
                    ) {

                        self.cursorPoint = [

                            e.lngLat.lng,

                            e.lngLat.lat
                        ];


                        self.updateDrawLayer();
                    }

                }
            );


            self.map.on(
                'mouseup',
                function() {

                    if (self.isDraggingVertex) {

                        self.isDraggingVertex = false;

                        self.draggedVertexIndex = null;

                        self.map.dragPan.enable();

                        self.map
                            .getCanvas()
                            .style
                            .cursor = '';
                    }

                }
            );


            self.map.on(
                'mouseout',
                function() {

                    if (
                        self.cursorPoint &&
                        !self.isDraggingVertex
                    ) {

                        self.cursorPoint = null;

                        self.updateDrawLayer();
                    }

                }
            );


            // =================================================
            // MAP CLICK
            // =================================================

            self.map.on(
                'click',
                function(e) {

                    if (
                        self.showModal() ||
                        self.isDraggingVertex
                    ) {
                        return;
                    }


                    var lng = e.lngLat.lng;

                    var lat = e.lngLat.lat;


                    // -----------------------------------------
                    // POINT MODE
                    // -----------------------------------------

                    if (
                        self.drawingMode() === 'point'
                    ) {

                        if (self.marker) {

                            self.marker.remove();
                        }


                        self.marker =
                            new mapboxgl.Marker({
                                color: '#FF0000'
                            })
                            .setLngLat([
                                lng,
                                lat
                            ])
                            .addTo(self.map);


                        var pointFeature = {

                            geometry: {

                                coordinates: [
                                    lng,
                                    lat
                                ],

                                type: 'Point'
                            },

                            type: 'Feature'
                        };


                        self.prepareModal(
                            pointFeature,
                            'Point'
                        );

                    }


                    // -----------------------------------------
                    // POLYGON MODE
                    // -----------------------------------------

                    else if (
                        self.drawingMode() === 'polygon'
                    ) {

                        if (self.isPolygonClosed()) {

                            return;
                        }


                        var pts =
                            self.polygonPoints();


                        if (pts.length >= 3) {

                            var firstPt =
                                pts[0];


                            var screenFirstPt =
                                self.map.project(
                                    firstPt
                                );


                            var screenClickPt =
                                e.point;


                            var distance =
                                Math.sqrt(

                                    Math.pow(
                                        screenClickPt.x -
                                        screenFirstPt.x,
                                        2
                                    )

                                    +

                                    Math.pow(
                                        screenClickPt.y -
                                        screenFirstPt.y,
                                        2
                                    )
                                );


                            if (distance < 20) {

                                self.closePolygon();

                                return;
                            }

                        }


                        self.polygonPoints.push([
                            lng,
                            lat
                        ]);


                        self.updateDrawLayer();

                    }

                }
            );


            // =================================================
            // DOUBLE CLICK CLOSE POLYGON
            // =================================================

            self.map.on(
                'dblclick',
                function(e) {

                    if (
                        self.drawingMode() === 'polygon' &&
                        self.polygonPoints().length >= 3
                    ) {

                        e.preventDefault();

                        self.closePolygon();
                    }

                }
            );


            // =================================================
            // RIGHT CLICK CLOSE POLYGON
            // =================================================

            self.map.on(
                'contextmenu',
                function(e) {

                    if (
                        self.drawingMode() === 'polygon' &&
                        self.polygonPoints().length >= 3
                    ) {

                        if (e.originalEvent) {

                            e.originalEvent
                                .preventDefault();
                        }


                        self.closePolygon();
                    }

                }
            );


            // =================================================
            // MAP RESIZE FIX
            // =================================================

            var resizeCount = 0;


            var forceResize =
                setInterval(
                    function() {

                        if (self.map) {

                            self.map.resize();
                        }


                        resizeCount++;


                        if (resizeCount > 10) {

                            clearInterval(
                                forceResize
                            );
                        }

                    },
                    100
                );

        };


        // =====================================================
        // GEOMETRY / COORDINATE LOOKUP
        // =====================================================

        self.lookupGeometry = function() {

            var rawQuery =
                self.geometrySearchQuery()
                    .trim();


            if (!rawQuery) {
                return;
            }


            if (self.searchMarker) {

                self.searchMarker.remove();
            }


            if (
                self.map &&
                self.map.getSource(
                    'search-highlight-source'
                )
            ) {

                self.map
                    .getSource(
                        'search-highlight-source'
                    )
                    .setData({

                        type:
                            'FeatureCollection',

                        features: []
                    });
            }


            try {

                // ---------------------------------------------
                // GEOJSON
                // ---------------------------------------------

                if (
                    rawQuery.startsWith('{')
                ) {

                    var parsedObj =
                        JSON.parse(rawQuery);


                    var geometryObj =
                        parsedObj.geometry ||
                        parsedObj;


                    if (
                        !geometryObj.type ||
                        !geometryObj.coordinates
                    ) {

                        alert(
                            "Invalid structure. Ensure your JSON contains 'type' and 'coordinates' keys."
                        );

                        return;
                    }


                    var allCoordinates = [];


                    var processCoords =
                        function(coords, type) {

                            if (
                                type === 'Point'
                            ) {

                                allCoordinates.push(
                                    coords
                                );
                            }

                            else if (
                                type === 'LineString' ||
                                type === 'MultiPoint'
                            ) {

                                allCoordinates =
                                    allCoordinates.concat(
                                        coords
                                    );
                            }

                            else if (
                                type === 'Polygon' ||
                                type === 'MultiLineString'
                            ) {

                                coords.forEach(
                                    function(r) {

                                        allCoordinates =
                                            allCoordinates.concat(
                                                r
                                            );
                                    }
                                );
                            }

                            else if (
                                type === 'MultiPolygon'
                            ) {

                                coords.forEach(
                                    function(p) {

                                        p.forEach(
                                            function(r) {

                                                allCoordinates =
                                                    allCoordinates.concat(
                                                        r
                                                    );
                                            }
                                        );
                                    }
                                );
                            }

                        };


                    processCoords(
                        geometryObj.coordinates,
                        geometryObj.type
                    );


                    if (
                        allCoordinates.length === 0
                    ) {

                        return;
                    }


                    var minLng =
                        allCoordinates[0][0];

                    var maxLng =
                        allCoordinates[0][0];

                    var minLat =
                        allCoordinates[0][1];

                    var maxLat =
                        allCoordinates[0][1];


                    allCoordinates.forEach(
                        function(pt) {

                            if (
                                pt[0] < minLng
                            ) {

                                minLng = pt[0];
                            }


                            if (
                                pt[0] > maxLng
                            ) {

                                maxLng = pt[0];
                            }


                            if (
                                pt[1] < minLat
                            ) {

                                minLat = pt[1];
                            }


                            if (
                                pt[1] > maxLat
                            ) {

                                maxLat = pt[1];
                            }

                        }
                    );


                    var highlightFeature = {

                        type: 'Feature',

                        geometry: geometryObj
                    };


                    self.map
                        .getSource(
                            'search-highlight-source'
                        )
                        .setData({

                            type:
                                'FeatureCollection',

                            features: [
                                highlightFeature
                            ]
                        });


                    if (
                        geometryObj.type === 'Point'
                    ) {

                        self.map.flyTo({

                            center: [
                                minLng,
                                minLat
                            ],

                            zoom: 15
                        });

                    }

                    else {

                        self.map.fitBounds(
                            [
                                [
                                    minLng,
                                    minLat
                                ],

                                [
                                    maxLng,
                                    maxLat
                                ]
                            ],
                            {

                                padding: 60,

                                duration: 1500
                            }
                        );

                    }

                }


                // ---------------------------------------------
                // PLAIN LONGITUDE / LATITUDE
                // ---------------------------------------------

                else {

                    var matches =
                        rawQuery.match(
                            /[-+]?[0-9]*\.?[0-9]+/g
                        );


                    if (
                        !matches ||
                        matches.length < 2
                    ) {

                        alert(
                            'Could not parse coordinates. Format as: Longitude, Latitude'
                        );

                        return;
                    }


                    var lng =
                        parseFloat(
                            matches[0]
                        );


                    var lat =
                        parseFloat(
                            matches[1]
                        );


                    self.searchMarker =
                        new mapboxgl.Marker({
                            color: '#ffea00'
                        })
                        .setLngLat([
                            lng,
                            lat
                        ])
                        .addTo(self.map);


                    self.map.flyTo({

                        center: [
                            lng,
                            lat
                        ],

                        zoom: 14,

                        duration: 1500
                    });

                }

            }

            catch (err) {

                console.error(
                    'Lookup syntax failure:',
                    err
                );


                alert(
                    'Parsing error. Verify your JSON configuration or coordinate string values.'
                );

            }

        };


        // =====================================================
        // UPDATE DRAW LAYER
        // =====================================================

        self.updateDrawLayer = function() {

            if (
                !self.map ||
                !self.map.getSource(
                    'draw-source'
                )
            ) {

                return;
            }


            var activePoints =
                self.polygonPoints()
                    .slice();


            if (
                self.cursorPoint &&
                self.drawingMode() === 'polygon' &&
                !self.isPolygonClosed()
            ) {

                activePoints.push(
                    self.cursorPoint
                );
            }


            var features = [];


            if (
                activePoints.length >= 3
            ) {

                var closedPoly =
                    activePoints.slice();


                closedPoly.push(
                    activePoints[0]
                );


                features.push({

                    type: 'Feature',

                    geometry: {

                        type: 'Polygon',

                        coordinates: [
                            closedPoly
                        ]
                    }
                });

            }

            else if (
                activePoints.length > 1
            ) {

                features.push({

                    type: 'Feature',

                    geometry: {

                        type: 'LineString',

                        coordinates:
                            activePoints
                    }
                });

            }


            self.polygonPoints()
                .forEach(
                    function(pt, index) {

                        features.push({

                            type: 'Feature',

                            id: index,

                            geometry: {

                                type: 'Point',

                                coordinates: pt
                            }
                        });

                    }
                );


            self.map
                .getSource(
                    'draw-source'
                )
                .setData({

                    type:
                        'FeatureCollection',

                    features:
                        features
                });


            if (
                self.polygonPoints()
                    .length > 0
            ) {

                self.map.setFeatureState(
                    {

                        source:
                            'draw-source',

                        id: 0
                    },
                    {

                        isFirst: true
                    }
                );
            }

        };


        // =====================================================
        // CLEAR CURRENT DRAWING
        // =====================================================

        self.clearMap = function() {

            if (self.marker) {

                self.marker.remove();
            }


            if (self.searchMarker) {

                self.searchMarker.remove();
            }


            if (
                self.map &&
                self.map.getSource(
                    'search-highlight-source'
                )
            ) {

                self.map
                    .getSource(
                        'search-highlight-source'
                    )
                    .setData({

                        type:
                            'FeatureCollection',

                        features: []
                    });
            }


            self.polygonPoints([]);

            self.cursorPoint = null;

            self.isPolygonClosed(false);

            self.updateDrawLayer();

        };


        // =====================================================
        // CLOSE POLYGON
        // =====================================================

        self.closePolygon = function() {

            if (
                self.polygonPoints()
                    .length < 3
            ) {

                return;
            }


            var pts =
                self.polygonPoints();


            if (
                pts.length > 2
            ) {

                var last =
                    pts[
                        pts.length - 1
                    ];


                var secondLast =
                    pts[
                        pts.length - 2
                    ];


                if (
                    last[0] === secondLast[0] &&
                    last[1] === secondLast[1]
                ) {

                    self.polygonPoints.pop();
                }

            }


            self.isPolygonClosed(true);

            self.cursorPoint = null;

            self.updateDrawLayer();

        };


        // =====================================================
        // PREPARE POLYGON FOR SAVE
        // =====================================================

        self.triggerPolygonSave = function() {

            if (
                self.polygonPoints()
                    .length < 3
            ) {

                return;
            }


            if (
                !self.isPolygonClosed()
            ) {

                self.closePolygon();
            }


            var pts =
                self.polygonPoints()
                    .slice();


            pts.push(
                pts[0]
            );


            var polygonFeature = {

                geometry: {

                    coordinates: [
                        pts
                    ],

                    type: 'Polygon'
                },

                type: 'Feature'
            };


            self.prepareModal(
                polygonFeature,
                'Polygon'
            );

        };


        // =====================================================
        // PREPARE MODAL
        // =====================================================

        self.prepareModal =
            function(feature, typeName) {

                self.isSaving(false);

                self.saveSuccess(false);

                self.currentFeature(
                    feature
                );

                self.featureType(
                    typeName
                );

                self.coordinateDisplay(
                    JSON.stringify(
                        feature.geometry
                    )
                );

                self.showModal(true);

            };


        // =====================================================
        // CLOSE MODAL
        // =====================================================

        self.closeModal = function() {

            self.showModal(false);


            if (
                !self.saveSuccess()
            ) {

                self.clearMap();
            }

        };


        // =====================================================
        // CONFIRM SAVE
        // =====================================================

        self.confirmSave = function() {

            self.isSaving(true);

            self.createResource(
                self.currentFeature()
            );

        };


        // =====================================================
        // CREATE ARCHES RESOURCE
        // =====================================================

        self.createResource =
            function(featureGeoJSON) {

                featureGeoJSON.id =
                    self.generateUUID();


                if (
                    !featureGeoJSON.properties
                ) {

                    featureGeoJSON.properties = {};
                }


                var tileData = {};


                tileData[
                    self.spatialNodeId
                ] = {

                    type:
                        'FeatureCollection',

                    features: [
                        featureGeoJSON
                    ]
                };


                new TileModel({

                    nodegroup_id:
                        self.spatialNodeGroupId,

                    data:
                        tileData

                })
                .save()

                .done(
                    function(response) {

                        var id =
                            response.resourceinstance_id ||

                            (
                                response.data &&
                                response.data.resourceinstance_id
                            );


                        if (!id) {

                            alert(
                                "Saved successfully, but couldn't find the new Resource ID."
                            );

                            self.isSaving(false);

                            return;
                        }


                        self.savedResourceId(
                            id
                        );


                        self.savedResourceUrl(

                            arches.urls.root +

                            'resource/' +

                            id
                        );


                        self.saveSuccess(true);

                        self.isSaving(false);

                    }
                )

                .fail(
                    function(xhr) {

                        console.error(
                            'Native Tile Save Failed:',
                            xhr.responseText
                        );


                        alert(
                            'Failed to save. Check the F12 Console.'
                        );


                        self.isSaving(false);

                    }
                );

            };


        // =====================================================
        // WAIT FOR MAP CONTAINER
        // =====================================================

        var checkExist =
            setInterval(
                function() {

                    if (
                        $('#plugin-map-container')
                            .length
                    ) {

                        self.initMap();

                        clearInterval(
                            checkExist
                        );
                    }

                },
                100
            );

    };


    // =========================================================
    // EAMENA QUICK PIN COMPONENT
    // =========================================================

    return ko.components.register(
        'eamena-quick-pin',
        {
            viewModel: QuickPinViewModel,

            template: `

<div
    style="
        position: relative;
        width: 100%;
        min-height: 650px;
        box-sizing: border-box;
        overflow: hidden;
        background: #eef0f2;
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            'Segoe UI',
            Roboto,
            Helvetica,
            Arial,
            sans-serif;
    "
>

    <!-- =====================================================
         MAP
         ===================================================== -->

    <div
        id="plugin-map-container"
        style="
            width: 100%;
            height: 82vh;
            min-height: 650px;
            background: #e8eaed;
        "
    ></div>


    <!-- =====================================================
         TOP TOOLBAR
         ===================================================== -->

    <div
        style="
            position: absolute;
            top: 18px;
            left: 18px;
            right: 70px;
            z-index: 10;
            pointer-events: none;
        "
    >

        <div
            style="
                display: inline-flex;
                flex-direction: row;
                flex-wrap: nowrap;
                align-items: center;
                gap: 7px;

                min-height: 50px;
                box-sizing: border-box;
                padding: 6px;

                background: rgba(255,255,255,0.96);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);

                border: 1px solid rgba(20,25,30,0.08);
                border-radius: 13px;

                box-shadow: 0 4px 18px rgba(0,0,0,0.14);

                pointer-events: auto;
                white-space: nowrap;
            "
        >

            <!-- =============================================
                 QUICK PIN BRAND
                 ============================================= -->

            <div
                style="
                    display: inline-flex;
                    align-items: center;
                    gap: 9px;

                    height: 36px;
                    flex: 0 0 auto;

                    padding: 0 12px 0 5px;

                    border-right: 1px solid #e4e6e9;
                "
            >

                <div
                    style="
                        width: 29px;
                        height: 29px;

                        display: flex;
                        align-items: center;
                        justify-content: center;

                        flex: 0 0 29px;

                        border-radius: 8px;

                        background: #7078ecd9;
                        color: #ffffff;
                    "
                >

                    <svg
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path
                            d="
                                M20 10
                                c0 5-8 11-8 11
                                S4 15 4 10
                                a8 8 0 1 1 16 0z
                            "
                        ></path>

                        <circle
                            cx="12"
                            cy="10"
                            r="2.5"
                        ></circle>
                    </svg>

                </div>

                <div
                    style="
                        line-height: 1.15;
                        white-space: nowrap;
                    "
                >
                    <div
                        style="
                            color: #202124;
                            font-size: 13px;
                            font-weight: 700;
                        "
                    >
                        Quick Pin
                    </div>

                    <div
                        style="
                            margin-top: 2px;
                            color: #8b9097;
                            font-size: 10px;
                            font-weight: 500;
                        "
                    >
                        Heritage Place
                    </div>
                </div>

            </div>


            <!-- =============================================
                 POINT
                 ============================================= -->

            <button
                type="button"
                title="Create a point"

                data-bind="
                    click: function(){
                        drawingMode('point');
                        clearMap();
                    },

                    style: {
                        background:
                            drawingMode() === 'point'
                                ? '#6b89e3'
                                : 'transparent',

                        color:
                            drawingMode() === 'point'
                                ? '#ffffff'
                                : '#2b2424'
                    }
                "

                style="
                    height: 36px;

                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 7px;

                    flex: 0 0 auto;

                    padding: 0 12px;

                    border: none;
                    border-radius: 8px;

                    cursor: pointer;

                    font-size: 12px;
                    font-weight: 650;

                    white-space: nowrap;
                "
            >

                <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <path
                        d="
                            M20 10
                            c0 5-8 11-8 11
                            S4 15 4 10
                            a8 8 0 1 1 16 0z
                        "
                    ></path>

                    <circle
                        cx="12"
                        cy="10"
                        r="2.5"
                    ></circle>
                </svg>

                <span>Point</span>

            </button>


            <!-- =============================================
                 POLYGON
                 ============================================= -->

            <button
                type="button"
                title="Draw a polygon"

                data-bind="
                    click: function(){
                        drawingMode('polygon');
                        clearMap();
                    },

                    style: {
                        background:
                            drawingMode() === 'polygon'
                                ? '#6b89e3'
                                : 'transparent',

                        color:
                            drawingMode() === 'polygon'
                                ? '#ffffff'
                                : '#2b2424'
                    }
                "

                style="
                    height: 36px;

                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 7px;

                    flex: 0 0 auto;

                    padding: 0 12px;

                    border: none;
                    border-radius: 8px;

                    cursor: pointer;

                    font-size: 12px;
                    font-weight: 650;

                    white-space: nowrap;
                "
            >

                <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <path
                        d="
                            M7 3
                            h10
                            l5 8
                            -5 10
                            H7
                            L2 11
                            7 3z
                        "
                    ></path>
                </svg>

                <span>Polygon</span>

            </button>


            <!-- =============================================
                 DIVIDER
                 ============================================= -->

            <div
                style="
                    width: 1px;
                    height: 25px;
                    flex: 0 0 1px;
                    margin: 0 2px;
                    background: #e4e6e9;
                "
            ></div>


            <!-- =============================================
                 GEOMETRY SEARCH
                 ============================================= -->

            <div
                style="
                    width: 360px;
                    height: 36px;

                    flex: 0 0 360px;

                    display: flex;
                    flex-direction: row;
                    flex-wrap: nowrap;
                    align-items: center;

                    box-sizing: border-box;
                    overflow: hidden;

                    background: #f4f5f7;

                    border: 1px solid #e1e4e7;
                    border-radius: 8px;
                "
            >

                <!-- SEARCH ICON -->

                <div
                    style="
                        width: 34px;
                        height: 100%;

                        flex: 0 0 34px;

                        display: flex;
                        align-items: center;
                        justify-content: center;

                        color: #858a92;
                    "
                >

                    <svg
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <circle
                            cx="11"
                            cy="11"
                            r="7"
                        ></circle>

                        <path
                            d="m20 20-4-4"
                        ></path>
                    </svg>

                </div>


                <!-- SEARCH INPUT -->

                <input
                    type="text"

                    data-bind="
                        value: geometrySearchQuery,
                        valueUpdate: 'input',
                        event: {
                            keyup: function(data, event) {
                                if (event.key === 'Enter') {
                                    lookupGeometry();
                                }

                                return true;
                            }
                        }
                    "

                    placeholder="Longitude, latitude or GeoJSON"

                    style="
                        display: block;

                        flex: 1 1 0;
                        width: 0;
                        min-width: 0;
                        height: 34px;

                        box-sizing: border-box;

                        padding: 0 10px 0 2px;

                        border: none;
                        outline: none;

                        background: transparent;

                        color: #30343a;

                        font-size: 12px;
                        line-height: 34px;

                        text-overflow: ellipsis;
                    "
                >


                <!-- LOCATE -->

                <button
                    type="button"
                    title="Locate geometry"

                    data-bind="
                        click: lookupGeometry
                    "

                    style="
                        height: 28px;

                        display: inline-flex;
                        align-items: center;
                        justify-content: center;

                        flex: 0 0 auto;

                        margin: 0 4px 0 0;

                        padding: 0 12px;

                        border: 1px solid #dfe2e5;
                        border-radius: 6px;

                        background: #ffffff;
                        color: #353a40;

                        box-shadow:
                            0 1px 2px
                            rgba(0,0,0,0.08);

                        cursor: pointer;

                        font-size: 11px;
                        font-weight: 650;

                        white-space: nowrap;
                    "
                >
                    Locate
                </button>

            </div>


            <!-- =============================================
                 POLYGON ACTIONS DIVIDER

                 Important:
                 These controls are INSIDE the same toolbar.
                 ============================================= -->

            <div
                data-bind="
                    visible:
                        drawingMode() === 'polygon' &&
                        polygonPoints().length >= 3
                "

                style="
                    width: 1px;
                    height: 25px;
                    flex: 0 0 1px;
                    margin: 0 2px;
                    background: #e4e6e9;
                "
            ></div>


            <!-- =============================================
                 POLYGON ACTIONS

                 Using contents means there is NO separate
                 flex box capable of stacking the buttons.
                 Both buttons become direct children of the
                 main horizontal toolbar.
                 ============================================= -->

            <!-- ko if:
                drawingMode() === 'polygon' &&
                polygonPoints().length >= 3
            -->


            <!-- CLEAR -->

            <button
                type="button"
                title="Clear polygon"

                data-bind="
                    click: clearMap
                "

                style="
                    height: 36px;

                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 7px;

                    flex: 0 0 auto;

                    padding: 0 12px;

                    border: 1px solid #e3e5e8;
                    border-radius: 8px;

                    background: #ffffff;
                    color: #b13c3c;

                    cursor: pointer;

                    font-size: 12px;
                    font-weight: 650;

                    white-space: nowrap;
                "
            >

                <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <path d="M3 6h18"></path>
                    <path d="M8 6V4h8v2"></path>
                    <path d="M19 6l-1 14H6L5 6"></path>
                    <path d="M10 11v5"></path>
                    <path d="M14 11v5"></path>
                </svg>

                <span>Clear</span>

            </button>


            <!-- SAVE POLYGON -->

            <button
                type="button"
                title="Save polygon"

                data-bind="
                    click: triggerPolygonSave
                "

                style="
                    height: 36px;

                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 7px;

                    flex: 0 0 auto;

                    padding: 0 13px;

                    border: none;
                    border-radius: 8px;

                    background: #176b4d;
                    color: #ffffff;

                    cursor: pointer;

                    font-size: 12px;
                    font-weight: 700;

                    white-space: nowrap;
                "
            >

                <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <path d="M20 6 9 17l-5-5"></path>
                </svg>

                <span>Save Polygon</span>

            </button>


            <!-- /ko -->

        </div>

    </div>

    <!-- =====================================================
         MAP LEGEND
         ===================================================== -->

    <div
        style="
            position: absolute;
            left: 18px;
            bottom: 24px;

            z-index: 10;

            display: flex;
            align-items: center;
            gap: 14px;

            padding: 8px 12px;

            background: rgba(255,255,255,0.94);

            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);

            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 9px;

            box-shadow:
                0 2px 10px
                rgba(0,0,0,0.12);

            color: #60656d;

            font-size: 10px;

            pointer-events: none;
        "
    >

        <span
            style="
                color: #34383e;
                font-weight: 700;
            "
        >
            Existing records
        </span>

        <span
            style="
                display: flex;
                align-items: center;
                gap: 5px;
            "
        >
            <span
                style="
                    width: 8px;
                    height: 8px;

                    border-radius: 50%;

                    background: #ffaa00;

                    border: 1px solid #ffffff;

                    box-shadow:
                        0 0 0 1px
                        rgba(0,0,0,0.15);
                "
            ></span>

            Point
        </span>

        <span
            style="
                display: flex;
                align-items: center;
                gap: 5px;
            "
        >
            <span
                style="
                    width: 10px;
                    height: 8px;

                    background:
                        rgba(123,97,239,0.35);

                    border:
                        1.5px solid #ffaa00;
                "
            ></span>

            Polygon
        </span>

    </div>


    <!-- =====================================================
         MODAL BACKDROP
         ===================================================== -->

    <div
        data-bind="
            style: {
                display:
                    showModal()
                        ? 'flex'
                        : 'none'
            }
        "

        style="
            position: absolute;
            inset: 0;

            z-index: 9999;

            display: none;

            align-items: center;
            justify-content: center;

            padding: 24px;

            box-sizing: border-box;

            background:
                rgba(18,21,26,0.48);

            backdrop-filter: blur(3px);
            -webkit-backdrop-filter: blur(3px);
        "
    >

        <div
            style="
                width: 100%;
                max-width: 460px;

                overflow: hidden;

                background: #ffffff;

                border:
                    1px solid
                    rgba(0,0,0,0.08);

                border-radius: 16px;

                box-shadow:
                    0 24px 70px rgba(0,0,0,0.24),
                    0 3px 10px rgba(0,0,0,0.08);
            "
        >

            <!-- =============================================
                 SAVE CONFIRMATION
                 ============================================= -->

            <div
                data-bind="
                    visible:
                        !saveSuccess()
                "
            >

                <div
                    style="
                        padding: 22px 24px 16px;
                    "
                >

                    <div
                        style="
                            width: 38px;
                            height: 38px;

                            display: flex;
                            align-items: center;
                            justify-content: center;

                            margin-bottom: 16px;

                            border-radius: 10px;

                            background: #eef2ff;
                            color: #4f5fbf;
                        "
                    >

                        <svg
                            width="19"
                            height="19"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            <path
                                d="
                                    M20 10
                                    c0 5-8 11-8 11
                                    S4 15 4 10
                                    a8 8 0 1 1 16 0z
                                "
                            ></path>

                            <circle
                                cx="12"
                                cy="10"
                                r="2.5"
                            ></circle>
                        </svg>

                    </div>

                    <h3
                        style="
                            margin: 0;

                            color: #202124;

                            font-size: 18px;
                            font-weight: 700;

                            letter-spacing: -0.2px;
                        "
                    >
                        Save Heritage Place?
                    </h3>

                    <p
                        style="
                            margin: 7px 0 0;

                            color: #747981;

                            font-size: 13px;
                            line-height: 1.5;
                        "
                    >
                        Review the geometry before creating the
                        Heritage Place record.
                    </p>


                    <!-- GEOMETRY SUMMARY -->

                    <div
                        style="
                            margin-top: 20px;

                            overflow: hidden;

                            border: 1px solid #e7e9ec;
                            border-radius: 10px;
                        "
                    >

                        <div
                            style="
                                display: flex;
                                align-items: center;
                                justify-content: space-between;

                                padding: 10px 12px;

                                background: #f7f8f9;

                                border-bottom:
                                    1px solid #e7e9ec;
                            "
                        >

                            <span
                                style="
                                    color: #767b83;

                                    font-size: 11px;
                                    font-weight: 600;
                                "
                            >
                                Geometry type
                            </span>

                            <span
                                data-bind="
                                    text:
                                        featureType
                                "

                                style="
                                    padding: 3px 8px;

                                    border-radius: 20px;

                                    background: #eceef1;

                                    color: #373b41;

                                    font-size: 10px;
                                    font-weight: 700;
                                "
                            ></span>

                        </div>

                        <div
                            style="
                                padding: 12px;
                            "
                        >

                            <div
                                style="
                                    margin-bottom: 7px;

                                    color: #8a8f97;

                                    font-size: 10px;
                                    font-weight: 700;

                                    text-transform: uppercase;

                                    letter-spacing: 0.5px;
                                "
                            >
                                Geometry payload
                            </div>

                            <div
                                data-bind="
                                    text:
                                        coordinateDisplay
                                "

                                style="
                                    max-height: 125px;

                                    overflow-y: auto;

                                    padding: 10px;

                                    border-radius: 7px;

                                    background: #f7f8fa;

                                    color: #50545a;

                                    font-family:
                                        SFMono-Regular,
                                        Consolas,
                                        'Liberation Mono',
                                        monospace;

                                    font-size: 10px;
                                    line-height: 1.55;

                                    word-break: break-all;
                                "
                            ></div>

                        </div>

                    </div>

                </div>


                <!-- CONFIRMATION ACTIONS -->

                <div
                    style="
                        display: flex;
                        justify-content: flex-end;
                        gap: 8px;

                        padding: 14px 24px;

                        background: #fafafa;

                        border-top: 1px solid #eceef0;
                    "
                >

                    <button
                        data-bind="
                            click:
                                closeModal,

                            disable:
                                isSaving
                        "

                        style="
                            height: 36px;

                            padding: 0 14px;

                            border: 1px solid #dfe2e5;
                            border-radius: 8px;

                            background: #ffffff;

                            color: #4b5057;

                            cursor: pointer;

                            font-size: 12px;
                            font-weight: 600;
                        "
                    >
                        Cancel
                    </button>

                    <button
                        data-bind="
                            click:
                                confirmSave,

                            disable:
                                isSaving
                        "

                        style="
                            height: 36px;
                            min-width: 118px;

                            padding: 0 15px;

                            border: none;
                            border-radius: 8px;

                            background: #202124;
                            color: #ffffff;

                            cursor: pointer;

                            font-size: 12px;
                            font-weight: 650;
                        "
                    >

                        <span
                            data-bind="
                                text:
                                    isSaving()
                                        ? 'Saving...'
                                        : 'Save Geometry'
                            "
                        ></span>

                    </button>

                </div>

            </div>


            <!-- =============================================
                 SUCCESS STATE
                 ============================================= -->

            <div
                data-bind="
                    visible:
                        saveSuccess()
                "

                style="
                    display: none;
                "
            >

                <div
                    style="
                        padding: 28px 24px 22px;

                        text-align: center;
                    "
                >

                    <div
                        style="
                            width: 46px;
                            height: 46px;

                            margin: 0 auto 15px;

                            display: flex;
                            align-items: center;
                            justify-content: center;

                            border-radius: 50%;

                            background: #e8f5ee;

                            color: #247a52;
                        "
                    >

                        <svg
                            width="22"
                            height="22"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2.2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            <path
                                d="
                                    M20 6
                                    9 17
                                    l-5-5
                                "
                            ></path>
                        </svg>

                    </div>

                    <h3
                        style="
                            margin: 0;

                            color: #202124;

                            font-size: 18px;
                            font-weight: 700;
                        "
                    >
                        Heritage Place created
                    </h3>

                    <p
                        style="
                            max-width: 340px;

                            margin: 7px auto 0;

                            color: #777c84;

                            font-size: 13px;
                            line-height: 1.5;
                        "
                    >
                        The geometry has been saved and a draft
                        Heritage Place record is ready to review.
                    </p>


                    <div
                        style="
                            margin-top: 20px;

                            padding: 11px 12px;

                            background: #f6f7f8;

                            border: 1px solid #e6e8ea;
                            border-radius: 9px;

                            text-align: left;
                        "
                    >

                        <div
                            style="
                                margin-bottom: 5px;

                                color: #8a8f97;

                                font-size: 9px;
                                font-weight: 700;

                                text-transform: uppercase;

                                letter-spacing: 0.6px;
                            "
                        >
                            Resource UUID
                        </div>

                        <div
                            data-bind="
                                text:
                                    savedResourceId
                            "

                            style="
                                color: #3d4147;

                                font-family:
                                    SFMono-Regular,
                                    Consolas,
                                    monospace;

                                font-size: 11px;

                                word-break: break-all;
                            "
                        ></div>

                    </div>

                </div>


                <!-- SUCCESS ACTIONS -->

                <div
                    style="
                        display: flex;
                        justify-content: flex-end;
                        gap: 8px;

                        padding: 14px 24px;

                        background: #fafafa;

                        border-top: 1px solid #eceef0;
                    "
                >

                    <button
                        data-bind="
                            click:
                                closeModal
                        "

                        style="
                            height: 36px;

                            padding: 0 14px;

                            border: 1px solid #dfe2e5;
                            border-radius: 8px;

                            background: #ffffff;

                            color: #4b5057;

                            cursor: pointer;

                            font-size: 12px;
                            font-weight: 600;
                        "
                    >
                        Close
                    </button>

                    <a
                        data-bind="
                            attr: {
                                href:
                                    savedResourceUrl
                            }
                        "

                        style="
                            height: 36px;

                            display: inline-flex;
                            align-items: center;
                            gap: 7px;

                            padding: 0 15px;

                            border-radius: 8px;

                            background: #202124;
                            color: #ffffff;

                            text-decoration: none;

                            font-size: 12px;
                            font-weight: 650;
                        "
                    >

                        <span>Open Record</span>

                        <svg
                            width="13"
                            height="13"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            <path d="M7 17 17 7"></path>
                            <path d="M7 7h10v10"></path>
                        </svg>

                    </a>

                </div>

            </div>

        </div>

    </div>

</div>

            `
        }
    );

});
