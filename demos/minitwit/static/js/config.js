(function () {
    "use strict";
    var app = angular.module('aiohttp_admin', ['ng-admin']);

    app.config(['RestangularProvider', function(RestangularProvider) {
        RestangularProvider.addFullRequestInterceptor(
            function(element, operation, what, url, headers, params) {
            if (operation == 'getList') {
                if (params._sortField == 'id'){
                    params._sortField = '_id';}
            }
            return { params: params };
        });
    }]);


    app.config(['NgAdminConfigurationProvider', function (NgAdminConfigurationProvider) {
        var nga = NgAdminConfigurationProvider;

        var admin = nga.application('minitwit admin demo')
            .debug(true)
            .baseApiUrl('/admin/');

        var user = nga.entity('user')
            .identifier(nga.field('_id'));
        var message = nga.entity('message')
            .identifier(nga.field('_id'));
        var follower = nga.entity('follower')
            .identifier(nga.field('_id'));

        admin
            .addEntity(user)
            .addEntity(message)
            .addEntity(follower);

        user.listView()
            .title('Users')
            .description('List of users with infinite pagination')
            .infinitePagination(true)
            .perPage(10)
            .fields([
                nga.field('_id').label('_id'),
                nga.field('username', 'string'),
                nga.field('email', 'email'),
            ])
            .filters([
                nga.field('username')
                    .label('Find text')
                    .pinned(true)
                    .map(v => v && v['like'])
                    .transform(v => {return {'like': v};}),
            ])
            .listActions(['show', 'edit', 'delete']);

        user.creationView()
            .fields([
                nga.field('username'),
                nga.field('email'),
                nga.field('pw_hash'),
            ]);

        user.editionView()
            .fields(
                nga.field('_id')
                    .editable(false)
                    .label('_id'),
                user.creationView().fields()
            );

        user.deletionView()
            .title('Deletion confirmation');

        user.showView()
            .fields([
                nga.field('_id'),
                nga.field('username'),
                nga.field('email'),
                nga.field('pw_hash'),
            ]);

        message.listView()
            .title('Messages')
            .perPage(10)
            .fields([
                nga.field('_id'),
                nga.field('pub_date'),
            ])
            .filters([
                nga.field('name')
                    .label('Find text')
                    .pinned(true)
                    .map(v => v && v['like'])
                    .transform(v => {return {'like': v};}),
            ])
            .listActions(['edit', 'delete']);

        message.creationView()
            .fields([
                nga.field('text', 'wysiwyg'),
                nga.field('pub_date', 'date'),
                nga.field('author_id'),
            ]);

        message.editionView()
            .fields(
                nga.field('_id')
                    .editable(false)
                    .label('_id'),
                message.creationView().fields()
            );

        message.deletionView()
            .title('Deletion confirmation');

        follower.listView()
            .title('Messages')
            .perPage(10)
            .fields([
                nga.field('_id'),
                nga.field('who_id'),
                nga.field('whom_id'),
            ])
            .listActions(['edit', 'delete']);

        follower.creationView()
            .fields([
                nga.field('who_id'),
                nga.field('whom_id'),
            ]);

        follower.editionView()
            .fields(
                nga.field('_id')
                    .editable(false)
                    .label('_id'),
                follower.creationView().fields()
            );

        follower.deletionView()
            .title('Deletion confirmation');


        nga.configure(admin);
    }]);


}());
