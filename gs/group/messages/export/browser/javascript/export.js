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
    var postIds=null, toProcessIds=null, processedIds=null, currPost=null,
        posts=null, postsUrl=null, postUrl=null, GENERATED='generated_event';

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
        postIds = data;
        toProcessIds = data.slice(0);
        processedIds = [];
        posts = [];
        post_next();
    }//posts_request_success

    function error(jqXHR, textStatus, errorThrown) {
        console.error(errorThrown);
    }//error

    function post_next() {
        var pc=0;
        currPost = toProcessIds.pop();
        if (currPost) {
            send_post_request(currPost);
            pc = (((postIds.length - toProcessIds.length)
                   / (postIds.length * 1.0)) * 100);
            progressBar.css('width', pc.toString()+'%');
        } else {
            progressBar.trigger(GENERATED);
        }
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
        var blob=null;
        processedIds.push(currPost);
        blob = new Blob([data, '\n\n'], {type: 'text/plain'});
        posts.push(blob);
        post_next();
    }

    function post_request_error(jqXHR, textStatus, errorThrown) {
        console.error(errorThrown);
        post_next();
    }

    function get_posts_uri() {
        var retval=null, blob=null;
        blob = new Blob(posts, {type: 'text/plain'});
        retval = URL.createObjectURL(blob);
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
        get_save_url: function() {
            return get_posts_uri();
        },
        clear: function() {
            // Oi! Garbage collector! Over here!
            postIds = toProcessIds = processedIds = currPost = posts = null;
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
        var dataUri=null;
        save.removeAttr('disabled');
        // Close to utter madness
        dataUri = exporter.get_save_url();
        save.attr('href', dataUri);
        exporter.clear();
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
