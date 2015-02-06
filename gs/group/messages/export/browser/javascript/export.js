"use strict";
// Copyright © 2015 OnlineGroups.net and Contributors.
// All Rights Reserved.
//
// This software is subject to the provisions of the Zope Public License,
// Version 2.1 (ZPL). http://groupserver.org/downloads/license/
//
// THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
// WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
// FITNESS FOR A PARTICULAR PURPOSE.
jQuery.noConflict();

function GSGroupMessagesExport(progressBar, month, baseUrl) {
    var posts=null, toProcess=null, processed=null, currPost=null,
        postsUrl=null, postUrl=null, GENERATED='generated_event';

    function send_posts_request() {
        var settings=null;
        // The following is *mostly* a jQuery.post call:
        // jQuery.get(URL, d, success, 'application/json');
        settings = {
            accepts: 'application/json',
            async: true,
            cache: false,
            contentType: false,
            crossDomain: false,
            data: {month: month},
            processData: true,
            dataType: 'json',
            error: error,
            headers: {},
            success: posts_request_success,
            traditional: true,
            // timeout: TODO, What is the sane timeout?
            type: 'GET',
            url: postsUrl,
        };
        jQuery.ajax(settings);
    }//send_request

    function posts_request_success(data, textStatus, jqXHR) {
        posts = data;
        toProcess = data.slice(0);
        processed = []
        post_next();
    }//posts_request_success

    function error(jqXHR, textStatus, errorThrown) {
        console.error(errorThrown);
    }//error

    function post_next() {
        var pc=0;
        currPost = toProcess.pop();
        if (currPost) {
            send_post_request(currPost);
        } else {
            progressBar.trigger(GENERATED);
        }
        pc = ((posts.length - toProcess.length) / (posts.length * 1.0)) * 100;
        progressBar.css('width', pc.toString()+'%');
    }//post_next

    function send_post_request(postId) {
        var settings=null;
        // The following is *mostly* a jQuery.post call:
        // jQuery.get(URL, d, success, 'application/json');
        settings = {
            accepts: 'text/plain',
            async: true,
            cache: true, // Posts are immutable
            contentType: false,
            crossDomain: false,
            data: null,
            processData: false,
            dataType: 'text',
            error: post_request_error,
            headers: {},
            success: post_request_success,
            traditional: true,
            // timeout: TODO, What is the sane timeout?
            type: 'GET',
            url: postUrl + escape(postId),
        };
        jQuery.ajax(settings);
    }//send_post_request

    function post_request_success(data, textStatus, jqXHR) {
        sessionStorage.setItem(currPost, data);
        post_next();
    }

    function post_request_error(jqXHR, textStatus, errorThrown) {
        console.error(errorThrown);
        post_next();
    }

    function get_posts() {
        var retval=null, postId=null, post=null;
        for (var i in posts) {
            postId = posts[i];
            post = sessionStorage.getItem(postId);
            retval += post + '\r\n\r\n';
        }
        return retval;
    }

    function init() {
        postsUrl = baseUrl + 'gs-group-messages-export-posts.json';
        postUrl = baseUrl + 'gs-group-messages-export-mbox/';
    }//init
    init(); // Note the automatic execution

    return {
        generate: function () {
            send_posts_request();
        },
        save: function() {
            return get_posts();
        },
        clear: function() {
            var postId=null;
            for (var i in posts) {
                postId = posts[i];
                console.info(postId);
                sessionStorage.removeItem(postId);
            }
        },
        GENERATED_EVENT: GENERATED
    }
}

function gs_group_messages_export_click(event) {
    var month=null, generate=null, save=null, progress=null, progressBar=null,
        exporter=null;
    // Disable all the Generate buttons. No playing silly buggers.
    jQuery('.gs-group-messages-export-list-item-buttons-generate')
        .attr('disabled', 'disabled');

    generate = jQuery(event.target);

    // Show the progress bar
    progress = generate.parents('.gs-group-messages-export-list-item')
        .find('.progress');
    progress.removeClass('hide');

    // Set up the exporter
    progressBar = progress.find('.bar-progress');
    month = generate.data('month');
    exporter = GSGroupMessagesExport(progressBar, month, event.data);

    save = generate.parents('.gs-group-messages-export-list-item-buttons')
        .find('.gs-group-messages-export-list-item-buttons-save');

    progressBar.on(exporter.GENERATED_EVENT, function (event) {
        var data=null, dataUri=null;
        save.removeAttr('disabled');
        data = exporter.save();
        // Close to utter madness
        dataUri = 'data:text/plain;charset=utf-8,' + escape(data);
        exporter.clear();
        save.attr('href', dataUri);
        save.removeAttr('disabled');
        // Turn the Generate buttons on
        jQuery('.gs-group-messages-export-list-item-buttons-save[disabled]')
            .parents('.gs-group-messages-export-list-item-buttons')
            .find('.gs-group-messages-export-list-item-buttons-generate')
            .removeAttr('disabled');
        // For the one the person just cicked.
        generate.attr('disabled', 'disabled');
    });
    exporter.generate();
}

jQuery(window).load(function () {
    var messagesUrl=null;
    messagesUrl = jQuery('#gs-group-messages-export-script').data('url');
    jQuery('.gs-group-messages-export-list-item-buttons-generate')
        .click(messagesUrl, gs_group_messages_export_click);
});
